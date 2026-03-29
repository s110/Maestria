#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POT: Full Training — Paper-faithful parameters, no grid search.
Trains sequentially on: COCO-2017, Cityscapes, Mapillary Vistas v2.

Usage:
    python pot_full_training.py --base-dir .
    python pot_full_training.py --base-dir . --datasets coco cityscapes
"""

import argparse
import os
import json
import time
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader
from torchvision import transforms

# Import core POT components from existing script
from pot_cityscapes_colab import (
    # Constants
    SEED, K_CLUSTERS, CAM_THRESHOLD, THETA, LR_ENCODER, LR_EXTRA,
    FEAT_DIM, SINKHORN_REG, SINKHORN_ITERS,
    CITYSCAPES_CLASSES, COCO_CLASSES,
    # Datasets
    CityscapesWeakDataset, COCOWeakDataset, MapillaryWeakDataset,
    # Model
    POTEncoder,
    # POT pipeline
    pot_forward_single, cam_to_segmentation,
    # Losses
    classification_loss,
    # Utils
    polynomial_lr,
)

import warnings
warnings.filterwarnings('ignore')


# ═════════════════════════════════════════════════════════════════════════════
# Paper-faithful hyperparameters (Section 4.1)
# ═════════════════════════════════════════════════════════════════════════════

PAPER_CONFIG = {
    'img_size':    448,       # Standard WSSS resolution for ResNet50
    'batch_size':  16,        # Paper: "batch size of 16"
    'epochs':      6,         # Paper: "6 epochs"
    'num_workers': 8,
    'lr_encoder':  LR_ENCODER,  # 0.1
    'lr_extra':    LR_EXTRA,    # 1.0
    'K':           K_CLUSTERS,  # 3
    'tau':         CAM_THRESHOLD,  # 0.7
    'lambda':      THETA,      # 3.0
}


# ═════════════════════════════════════════════════════════════════════════════
# Training
# ═════════════════════════════════════════════════════════════════════════════

def train_one_epoch(model, loader, optimizer, epoch, global_step,
                    total_steps, device):
    model.train()
    sum_cls = 0.0
    sum_otcon = 0.0
    n = len(loader)

    for batch_idx, (images, img_labels, _) in enumerate(loader):
        images = images.to(device)
        img_labels = img_labels.to(device)

        lr_enc = polynomial_lr(global_step, total_steps)
        lr_ext = lr_enc * (LR_EXTRA / LR_ENCODER)
        optimizer.param_groups[0]['lr'] = lr_enc
        optimizer.param_groups[1]['lr'] = lr_ext

        logits, cam_cls, feats, _ = model(images)
        loss_cls = classification_loss(logits, img_labels)

        B, _, H, W = feats.shape
        batch_otcon = torch.tensor(0.0, device=device)
        for b in range(B):
            try:
                _, loss_b = pot_forward_single(
                    feats[b], cam_cls[b], img_labels[b], H, W)
                batch_otcon = batch_otcon + loss_b
            except Exception as e:
                if batch_idx == 0 and b == 0:
                    print(f'   [WARN] POT forward failed: {e}')
        batch_otcon = batch_otcon / B

        loss = loss_cls + THETA * batch_otcon
        optimizer.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=10.0)
        optimizer.step()
        global_step += 1

        sum_cls += loss_cls.item()
        sum_otcon += batch_otcon.item()

        if batch_idx % 100 == 0:
            print(f'   Epoch {epoch+1} [{batch_idx}/{n}] '
                  f'L_cls={loss_cls.item():.4f} '
                  f'L_otcon={batch_otcon.item():.4f} '
                  f'L_total={loss.item():.4f} '
                  f'LR={lr_enc:.6f}')

    return sum_cls / n, sum_otcon / n, global_step


def evaluate(model, loader, num_classes, device, max_samples=None):
    model.eval()
    intersection = np.zeros(num_classes)
    union = np.zeros(num_classes)
    correct = 0
    total_px = 0
    count = 0

    with torch.no_grad():
        for images, img_labels, masks_gt in loader:
            images = images.to(device)
            img_labels = img_labels.to(device)
            logits, cam_cls, feats, _ = model(images)
            B, _, H, W = feats.shape

            for b in range(B):
                gt = masks_gt[b].numpy()
                try:
                    cam_proto, _ = pot_forward_single(
                        feats[b], cam_cls[b], img_labels[b], H, W)
                    cam_up = F.interpolate(
                        cam_proto.unsqueeze(0), size=gt.shape,
                        mode='bilinear', align_corners=False).squeeze(0)
                    pred = cam_to_segmentation(cam_up).cpu().numpy() - 1
                except Exception:
                    pred = np.full(gt.shape, -1, dtype=np.int64)

                valid = (gt != 255)
                pv = pred[valid]
                gv = gt[valid]
                correct += (pv == gv).sum()
                total_px += valid.sum()

                for c in range(num_classes):
                    pc = (pv == c)
                    gc = (gv == c)
                    intersection[c] += (pc & gc).sum()
                    union[c] += (pc | gc).sum()
                count += 1

            if max_samples and count >= max_samples:
                break

    iou = np.where(union > 0, intersection / union, np.nan)
    return {
        'mIoU': float(np.nanmean(iou)),
        'PixelAcc': float(correct / max(total_px, 1)),
        'iou_per_class': iou.tolist(),
        'n_samples': count,
    }


# ═════════════════════════════════════════════════════════════════════════════
# Single dataset run
# ═════════════════════════════════════════════════════════════════════════════

def run_dataset(dataset_name, data_root, num_classes, class_names,
                output_dir, device, cfg):
    img_size = cfg['img_size']
    batch_size = cfg['batch_size']
    epochs = cfg['epochs']
    num_workers = cfg['num_workers']

    print(f'\n{"="*70}')
    print(f'  DATASET: {dataset_name.upper()} ({num_classes} clases)')
    print(f'  img_size={img_size} | batch_size={batch_size} | '
          f'epochs={epochs} | FULL dataset')
    print(f'{"="*70}')
    t0 = time.time()

    # Transforms
    train_tf = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])
    val_tf = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
    ])

    # Datasets — full, no subsets
    if dataset_name == 'cityscapes':
        train_ds = CityscapesWeakDataset(data_root, 'train', train_tf, img_size)
        val_ds = CityscapesWeakDataset(data_root, 'val', val_tf, img_size)
    elif dataset_name == 'mapillary_vistas_v2':
        train_ds = MapillaryWeakDataset(data_root, 'training', train_tf, img_size, num_classes)
        val_ds = MapillaryWeakDataset(data_root, 'validation', val_tf, img_size, num_classes)
    else:
        train_ds = COCOWeakDataset(data_root, 'train', train_tf, img_size, num_classes)
        val_ds = COCOWeakDataset(data_root, 'val', val_tf, img_size, num_classes)

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              num_workers=num_workers, pin_memory=True,
                              drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False,
                            num_workers=num_workers, pin_memory=True)

    print(f'  Train: {len(train_ds)} imagenes ({len(train_loader)} batches)')
    print(f'  Val:   {len(val_ds)} imagenes')

    # Model
    model = POTEncoder(num_classes=num_classes, feat_dim=FEAT_DIM).to(device)
    total_p = sum(p.numel() for p in model.parameters()) / 1e6
    print(f'  Modelo: {total_p:.1f}M parametros')

    encoder_params = (list(model.layer0.parameters()) +
                      list(model.layer1.parameters()) +
                      list(model.layer2.parameters()) +
                      list(model.layer3.parameters()) +
                      list(model.layer4.parameters()))
    extra_params = (list(model.hier_proj.parameters()) +
                    list(model.classifier.parameters()))

    optimizer = torch.optim.SGD([
        {'params': encoder_params, 'lr': cfg['lr_encoder']},
        {'params': extra_params, 'lr': cfg['lr_extra']},
    ], momentum=0.9, weight_decay=1e-4)

    total_steps = epochs * len(train_loader)
    global_step = 0
    history = []
    best_miou = 0.0

    # Training loop
    for epoch in range(epochs):
        t_ep = time.time()
        avg_cls, avg_otcon, global_step = train_one_epoch(
            model, train_loader, optimizer, epoch, global_step,
            total_steps, device)

        # Evaluate on 500 samples during training for speed
        metrics = evaluate(model, val_loader, num_classes, device,
                           max_samples=500)
        if metrics['mIoU'] > best_miou:
            best_miou = metrics['mIoU']

        elapsed = (time.time() - t_ep) / 60
        history.append({
            'epoch': epoch + 1,
            'L_cls': avg_cls,
            'L_otcon': avg_otcon,
            'mIoU': metrics['mIoU'],
            'PixelAcc': metrics['PixelAcc'],
            'minutes': elapsed,
        })

        print(f'  [Epoch {epoch+1}/{epochs}] '
              f'L_cls={avg_cls:.4f} L_otcon={avg_otcon:.4f} '
              f'mIoU={metrics["mIoU"]:.4f} '
              f'PixAcc={metrics["PixelAcc"]:.4f} '
              f'({elapsed:.1f} min)')

    # Full evaluation
    print(f'  Evaluacion final completa (val set entero)...')
    final = evaluate(model, val_loader, num_classes, device)

    elapsed_total = (time.time() - t0) / 60
    print(f'\n  RESULTADO FINAL [{dataset_name}]:')
    print(f'    mIoU     = {final["mIoU"]*100:.2f}%')
    print(f'    PixelAcc = {final["PixelAcc"]*100:.2f}%')
    print(f'    Tiempo   = {elapsed_total:.1f} min')

    # Per-class IoU
    print(f'\n  IoU por clase:')
    for i, name in enumerate(class_names):
        iou_val = final['iou_per_class'][i]
        if not np.isnan(iou_val):
            print(f'    {name:<30} {iou_val*100:>6.2f}%')
        else:
            print(f'    {name:<30}    N/A')

    # Save results
    os.makedirs(output_dir, exist_ok=True)
    result = {
        'dataset': dataset_name,
        'num_classes': num_classes,
        'config': cfg,
        'train_samples': len(train_ds),
        'val_samples': len(val_ds),
        'best_miou_during_training': best_miou,
        'final_mIoU': final['mIoU'],
        'final_PixelAcc': final['PixelAcc'],
        'iou_per_class': {name: final['iou_per_class'][i]
                          for i, name in enumerate(class_names)},
        'history': history,
        'elapsed_minutes': elapsed_total,
    }
    path = os.path.join(output_dir, f'full_training_{dataset_name}.json')
    with open(path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f'  Guardado: {path}')

    # Save model checkpoint
    ckpt_path = os.path.join(output_dir, f'model_{dataset_name}.pth')
    torch.save(model.state_dict(), ckpt_path)
    print(f'  Checkpoint: {ckpt_path}')

    return result


# ═════════════════════════════════════════════════════════════════════════════
# Main
# ═════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description='POT Full Training — Paper parameters, sequential datasets')
    parser.add_argument('--base-dir', type=str, default='.',
                        help='Base directory with dataset folders')
    parser.add_argument('--output-dir', type=str, default='./results/full_training',
                        help='Output directory')
    parser.add_argument('--datasets', nargs='+',
                        default=['coco', 'cityscapes', 'mapillary_vistas_v2'],
                        choices=['coco', 'cityscapes', 'mapillary_vistas_v2'],
                        help='Datasets to train (default: all three)')
    parser.add_argument('--img-size', type=int, default=448,
                        help='Image size (default: 448)')
    parser.add_argument('--batch-size', type=int, default=16,
                        help='Batch size (default: 16, paper value)')
    parser.add_argument('--epochs', type=int, default=6,
                        help='Epochs (default: 6, paper value)')
    parser.add_argument('--num-workers', type=int, default=8,
                        help='DataLoader workers (default: 8)')
    args = parser.parse_args()

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Dispositivo: {device}')
    if torch.cuda.is_available():
        print(f'GPU: {torch.cuda.get_device_name(0)}')
        print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')

    cfg = {
        'img_size': args.img_size,
        'batch_size': args.batch_size,
        'epochs': args.epochs,
        'num_workers': args.num_workers,
        'lr_encoder': LR_ENCODER,
        'lr_extra': LR_EXTRA,
        'K': K_CLUSTERS,
        'tau': CAM_THRESHOLD,
        'lambda': THETA,
    }

    print(f'\nConfiguracion (paper-faithful):')
    for k, v in cfg.items():
        print(f'  {k}: {v}')
    print(f'Datasets: {args.datasets}')

    # Dataset configs
    dataset_configs = {}

    if 'coco' in args.datasets:
        dataset_configs['coco'] = {
            'data_root': os.path.join(args.base_dir, 'coco_dataset'),
            'num_classes': 80,
            'class_names': COCO_CLASSES,
        }

    if 'cityscapes' in args.datasets:
        dataset_configs['cityscapes'] = {
            'data_root': os.path.join(args.base_dir, 'cityscapes'),
            'num_classes': 19,
            'class_names': CITYSCAPES_CLASSES,
        }

    if 'mapillary_vistas_v2' in args.datasets:
        mapillary_root = os.path.join(args.base_dir, 'mapillary_vistas_v2')
        config_path = os.path.join(mapillary_root, 'config_v2.0.json')
        with open(config_path, 'r') as f:
            mapillary_cfg = json.load(f)
        dataset_configs['mapillary_vistas_v2'] = {
            'data_root': mapillary_root,
            'num_classes': len(mapillary_cfg['labels']),
            'class_names': [l['readable'] for l in mapillary_cfg['labels']],
        }

    # Sequential training
    all_results = {}
    t_global = time.time()

    for ds_name, ds_cfg in dataset_configs.items():
        result = run_dataset(
            dataset_name=ds_name,
            data_root=ds_cfg['data_root'],
            num_classes=ds_cfg['num_classes'],
            class_names=ds_cfg['class_names'],
            output_dir=args.output_dir,
            device=device,
            cfg=cfg,
        )
        all_results[ds_name] = result

    # Summary
    total_time = (time.time() - t_global) / 60
    print(f'\n{"="*70}')
    print(f'  RESUMEN FINAL — Full Training')
    print(f'{"="*70}')
    print(f'  {"Dataset":<25} {"mIoU":>8} {"PixAcc":>8} {"Train":>8} {"Tiempo":>8}')
    print(f'  {"-"*60}')
    for ds, r in all_results.items():
        print(f'  {ds:<25} '
              f'{r["final_mIoU"]*100:>7.2f}% '
              f'{r["final_PixelAcc"]*100:>7.2f}% '
              f'{r["train_samples"]:>8} '
              f'{r["elapsed_minutes"]:>6.1f}m')
    print(f'\n  Tiempo total: {total_time:.1f} min')
    print(f'  Resultados en: {args.output_dir}')


if __name__ == '__main__':
    main()
