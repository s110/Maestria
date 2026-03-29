#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
POT: Prototypical Optimal Transport — SSH/SLURM Training Script
Supports: Cityscapes (19 classes) and COCO-2017 (80 classes)
Grid search over: IMG_SIZE × SUBSET_SIZE

Usage:
    python pot_cityscapes_colab.py --dataset cityscapes
    python pot_cityscapes_colab.py --dataset coco
"""

import argparse
import os
import sys
import json
import csv
import random
import time
import itertools
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader, Subset
from torchvision import transforms, models
from torchvision.models import ResNet50_Weights
from PIL import Image
from sklearn.cluster import KMeans
import warnings
warnings.filterwarnings('ignore')


# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 0 — CLI Arguments
# ═════════════════════════════════════════════════════════════════════════════

def parse_args():
    parser = argparse.ArgumentParser(
        description='POT: Prototypical Optimal Transport — SSH/SLURM Training')
    parser.add_argument('--dataset', type=str, required=True,
                        choices=['cityscapes', 'coco', 'mapillary_vistas_v2'],
                        help='Dataset: cityscapes, coco or mapillary_vistas_v2')
    parser.add_argument('--base-dir', type=str, default='.',
                        help='Base dir containing cityscapes/ and coco_dataset/ folders')
    parser.add_argument('--output-dir', type=str, default='./results',
                        help='Output directory for results')
    parser.add_argument('--epochs', type=int, default=6,
                        help='Training epochs per experiment (default: 6)')
    parser.add_argument('--batch-size', type=int, default=4,
                        help='Batch size (default: 4)')
    parser.add_argument('--num-workers', type=int, default=8,
                        help='DataLoader workers (default: 8)')
    return parser.parse_args()


# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 1 — Constantes e Hiperparámetros Fijos
# ═════════════════════════════════════════════════════════════════════════════

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed_all(SEED)

# Hiperparámetros fijos del paper (Sección 4.1)
K_CLUSTERS     = 3
CAM_THRESHOLD  = 0.7
THETA          = 3.0
LR_ENCODER     = 0.1
LR_EXTRA       = 1.0
FEAT_DIM       = 2048
SINKHORN_REG   = 0.1
SINKHORN_ITERS = 100

# ── Cityscapes: 19 clases ───────────────────────────────────────────────────

CITYSCAPES_CLASSES = [
    'road', 'sidewalk', 'building', 'wall', 'fence',
    'pole', 'traffic light', 'traffic sign', 'vegetation', 'terrain',
    'sky', 'person', 'rider', 'car', 'truck',
    'bus', 'train', 'motorcycle', 'bicycle'
]

CITYSCAPES_ID_TO_IDX = {
    7:0, 8:1, 11:2, 12:3, 13:4,
    17:5, 19:6, 20:7, 21:8, 22:9,
    23:10, 24:11, 25:12, 26:13, 27:14,
    28:15, 31:16, 32:17, 33:18
}

# ── COCO-2017: 80 clases ────────────────────────────────────────────────────

COCO_CAT_IDS = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17, 18, 19, 20, 21,
    22, 23, 24, 25, 27, 28, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42,
    43, 44, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61,
    62, 63, 64, 65, 67, 70, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 84,
    85, 86, 87, 88, 89, 90
]
COCO_CLASSES = [
    'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train',
    'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign',
    'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag',
    'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite',
    'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
    'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon',
    'bowl', 'banana', 'apple', 'sandwich', 'orange', 'broccoli', 'carrot',
    'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch', 'potted plant',
    'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote',
    'keyboard', 'cell phone', 'microwave', 'oven', 'toaster', 'sink',
    'refrigerator', 'book', 'clock', 'vase', 'scissors', 'teddy bear',
    'hair drier', 'toothbrush'
]
COCO_CAT_ID_TO_IDX = {cat_id: idx for idx, cat_id in enumerate(COCO_CAT_IDS)}


# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 2 — Datasets
# ═════════════════════════════════════════════════════════════════════════════

class CityscapesWeakDataset(Dataset):
    """Dataset de Cityscapes para supervisión débil (19 clases)."""

    def __init__(self, root, split='train', transform=None, img_size=224):
        self.root      = root
        self.split     = split
        self.transform = transform
        self.img_size  = img_size
        self.id_to_idx = CITYSCAPES_ID_TO_IDX
        self.num_classes = 19
        self.samples   = []
        self._build_file_list()

    def _build_file_list(self):
        img_dir = os.path.join(self.root, 'leftImg8bit', self.split)
        gt_dir  = os.path.join(self.root, 'gtFine', self.split)
        for city in sorted(os.listdir(img_dir)):
            city_img = os.path.join(img_dir, city)
            city_gt  = os.path.join(gt_dir, city)
            for fname in sorted(os.listdir(city_img)):
                if not fname.endswith('_leftImg8bit.png'):
                    continue
                prefix   = fname.replace('_leftImg8bit.png', '')
                gt_fname = prefix + '_gtFine_labelIds.png'
                img_path = os.path.join(city_img, fname)
                gt_path  = os.path.join(city_gt, gt_fname)
                if os.path.exists(gt_path):
                    self.samples.append((img_path, gt_path))
        print(f'   [{self.split}] {len(self.samples)} muestras cargadas (Cityscapes)')

    def _label_ids_to_idx(self, mask_pil):
        mask_np  = np.array(mask_pil, dtype=np.int32)
        out_mask = np.full(mask_np.shape, 255, dtype=np.uint8)
        for orig_id, idx in self.id_to_idx.items():
            out_mask[mask_np == orig_id] = idx
        return out_mask

    def _get_image_label(self, mask_idx):
        label  = torch.zeros(self.num_classes, dtype=torch.float32)
        unique = np.unique(mask_idx)
        for u in unique:
            if 0 <= u < self.num_classes:
                label[u] = 1.0
        return label

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, gt_path = self.samples[idx]
        image    = Image.open(img_path).convert('RGB')
        mask_pil = Image.open(gt_path)
        mask_idx = self._label_ids_to_idx(mask_pil)
        img_label = self._get_image_label(mask_idx)
        if self.transform:
            image = self.transform(image)
        mask_tensor = torch.from_numpy(
            np.array(Image.fromarray(mask_idx).resize(
                (self.img_size, self.img_size), Image.NEAREST))
        ).long()
        return image, img_label, mask_tensor


class COCOWeakDataset(Dataset):
    """Dataset de COCO-2017 para supervisión débil (80 clases)."""

    def __init__(self, root, split='train', transform=None, img_size=224, num_classes=80):
        from pycocotools.coco import COCO as COCOAPI
        self.root        = root
        self.split       = split
        self.transform   = transform
        self.img_size    = img_size
        self.num_classes = num_classes
        self.cat_id_to_idx = COCO_CAT_ID_TO_IDX

        ann_file = os.path.join(root, 'annotations', f'instances_{split}2017.json')
        print(f'   Cargando anotaciones COCO: {ann_file} ...')
        self.coco    = COCOAPI(ann_file)
        self.img_ids = sorted(self.coco.getImgIds())
        self.img_dir = os.path.join(root, f'{split}2017')
        print(f'   [{split}] {len(self.img_ids)} imágenes cargadas (COCO)')

    def __len__(self):
        return len(self.img_ids)

    def __getitem__(self, idx):
        img_id   = self.img_ids[idx]
        img_info = self.coco.loadImgs(img_id)[0]
        img_path = os.path.join(self.img_dir, img_info['file_name'])
        image    = Image.open(img_path).convert('RGB')

        ann_ids = self.coco.getAnnIds(imgIds=img_id)
        anns    = self.coco.loadAnns(ann_ids)

        # Image-level label
        img_label = torch.zeros(self.num_classes, dtype=torch.float32)
        for ann in anns:
            cid = ann['category_id']
            if cid in self.cat_id_to_idx:
                img_label[self.cat_id_to_idx[cid]] = 1.0

        # Segmentation mask (for evaluation)
        h, w = img_info['height'], img_info['width']
        mask  = np.full((h, w), 255, dtype=np.uint8)
        for ann in sorted(anns, key=lambda a: a['area'], reverse=True):
            cid = ann['category_id']
            if cid not in self.cat_id_to_idx:
                continue
            try:
                bm = self.coco.annToMask(ann)
                mask[bm == 1] = self.cat_id_to_idx[cid]
            except Exception:
                pass

        if self.transform:
            image = self.transform(image)

        mask_resized = np.array(
            Image.fromarray(mask).resize((self.img_size, self.img_size), Image.NEAREST))
        mask_tensor = torch.from_numpy(mask_resized).long()
        return image, img_label, mask_tensor


class MapillaryWeakDataset(Dataset):
    """Dataset de Mapillary Vistas v2 (124 clases para v2.0)."""

    def __init__(self, root, split='training', transform=None, img_size=224, num_classes=124):
        self.root        = root
        self.split       = split
        self.transform   = transform
        self.img_size    = img_size
        self.num_classes = num_classes
        self.samples     = []
        self._build_file_list()

    def _build_file_list(self):
        img_dir = os.path.join(self.root, self.split, 'images')
        gt_dir  = os.path.join(self.root, self.split, 'v2.0', 'labels')
        
        if not os.path.exists(img_dir) or not os.path.exists(gt_dir):
            print(f'   [ERROR] Rutas faltantes: {img_dir} o {gt_dir}')
            return

        for fname in sorted(os.listdir(img_dir)):
            if not (fname.endswith('.jpg') or fname.endswith('.png')):
                continue
            prefix   = os.path.splitext(fname)[0]
            gt_fname = prefix + '.png'
            img_path = os.path.join(img_dir, fname)
            gt_path  = os.path.join(gt_dir, gt_fname)
            if os.path.exists(gt_path):
                self.samples.append((img_path, gt_path))
        print(f'   [{self.split}] {len(self.samples)} muestras cargadas (Mapillary)')

    def _get_image_label(self, mask_idx):
        label  = torch.zeros(self.num_classes, dtype=torch.float32)
        unique = np.unique(mask_idx)
        for u in unique:
            if 0 <= u < self.num_classes:
                label[u] = 1.0
        return label

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, gt_path = self.samples[idx]
        image    = Image.open(img_path).convert('RGB')
        mask_pil = Image.open(gt_path)
        mask_idx = np.array(mask_pil, dtype=np.uint8)
        
        img_label = self._get_image_label(mask_idx)
        
        if self.transform:
            image = self.transform(image)
            
        mask_tensor = torch.from_numpy(
            np.array(Image.fromarray(mask_idx).resize(
                (self.img_size, self.img_size), Image.NEAREST))
        ).long()
        return image, img_label, mask_tensor


# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 3 — Arquitectura: Encoder (ResNet50) + Clasificador + CAM
# ═════════════════════════════════════════════════════════════════════════════

class HierarchicalProjection(nn.Module):
    """Proyección L(F1,F2,F3,F4) del paper (Eq. 2 y 8)."""
    def __init__(self, out_dim=2048):
        super().__init__()
        self.proj1 = nn.Conv2d(256,  out_dim, kernel_size=1, bias=False)
        self.proj2 = nn.Conv2d(512,  out_dim, kernel_size=1, bias=False)
        self.proj3 = nn.Conv2d(1024, out_dim, kernel_size=1, bias=False)
        self.proj4 = nn.Conv2d(2048, out_dim, kernel_size=1, bias=False)
        self.bn    = nn.BatchNorm2d(out_dim)
        self.relu  = nn.ReLU(inplace=True)

    def forward(self, f1, f2, f3, f4):
        H, W = f4.shape[2], f4.shape[3]
        p1 = F.interpolate(self.proj1(f1), size=(H, W), mode='bilinear', align_corners=False)
        p2 = F.interpolate(self.proj2(f2), size=(H, W), mode='bilinear', align_corners=False)
        p3 = F.interpolate(self.proj3(f3), size=(H, W), mode='bilinear', align_corners=False)
        p4 = self.proj4(f4)
        return self.relu(self.bn(p1 + p2 + p3 + p4))


class POTEncoder(nn.Module):
    """Encoder ResNet50 + clasificador + CAM generation."""
    def __init__(self, num_classes=19, feat_dim=FEAT_DIM):
        super().__init__()
        backbone = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
        self.layer0 = nn.Sequential(backbone.conv1, backbone.bn1,
                                    backbone.relu, backbone.maxpool)
        self.layer1 = backbone.layer1
        self.layer2 = backbone.layer2
        self.layer3 = backbone.layer3
        self.layer4 = backbone.layer4
        self.hier_proj  = HierarchicalProjection(out_dim=feat_dim)
        self.classifier = nn.Linear(feat_dim, num_classes, bias=False)
        self.num_classes = num_classes
        self.feat_dim    = feat_dim

    def forward(self, x):
        x  = self.layer0(x)
        f1 = self.layer1(x)
        f2 = self.layer2(f1)
        f3 = self.layer3(f2)
        f4 = self.layer4(f3)
        feats  = self.hier_proj(f1, f2, f3, f4)
        gap    = F.adaptive_avg_pool2d(feats, 1).flatten(1)
        logits = self.classifier(gap)
        W      = self.classifier.weight
        cam_fg = F.relu(torch.einsum('cd,bdhw->bchw', W, feats))
        cam_max = cam_fg.flatten(2).max(dim=2)[0].unsqueeze(-1).unsqueeze(-1) + 1e-8
        cam_fg  = cam_fg / cam_max
        cam_bg  = 1.0 - cam_fg.max(dim=1, keepdim=True)[0]
        cam_cls = torch.cat([cam_bg, cam_fg], dim=1)
        return logits, cam_cls, feats, (f1, f2, f3, f4)


# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 4 — POT Pipeline (Stage I, II, III)
# ═════════════════════════════════════════════════════════════════════════════

def mask_average_pool(features, mask):
    mask = mask.float()
    if mask.sum() < 1:
        return features.mean(dim=1)
    return (features * mask.unsqueeze(0)).sum(dim=1) / mask.sum()


def feature_partitioning(feats_flat, cam_cls, img_label, K=K_CLUSTERS,
                         threshold=CAM_THRESHOLD):
    D, HW    = feats_flat.shape
    C        = img_label.shape[0]
    J1       = C + 1
    feats_np = feats_flat.detach().T.cpu().numpy()

    cluster_protos = torch.zeros(J1, K, D, device=feats_flat.device)
    cls_protos     = torch.zeros(J1, D,    device=feats_flat.device)
    cluster_masks  = torch.zeros(HW, J1, K, device=feats_flat.device)
    present_classes = []

    # Background
    bg_cam  = cam_cls[0]
    bg_conf = (bg_cam > threshold).cpu().numpy()
    bg_mask_t = torch.from_numpy(bg_conf.astype(np.float32)).to(feats_flat.device)
    cls_protos[0] = mask_average_pool(feats_flat, bg_mask_t)
    if bg_conf.sum() >= K:
        try:
            km     = KMeans(n_clusters=K, n_init=3, random_state=SEED)
            labels = km.fit_predict(feats_np[bg_conf])
            conf_indices = np.where(bg_conf)[0]
            for k in range(K):
                k_indices = conf_indices[labels == k]
                if len(k_indices) > 0:
                    k_mask = torch.zeros(HW, device=feats_flat.device)
                    k_mask[k_indices] = 1.0
                    cluster_protos[0, k] = mask_average_pool(feats_flat, k_mask)
                    cluster_masks[:, 0, k] = k_mask
        except Exception:
            for k in range(K):
                cluster_protos[0, k] = cls_protos[0]
    else:
        for k in range(K):
            cluster_protos[0, k] = cls_protos[0]
    present_classes.append(0)

    # Foreground
    fg_present = torch.where(img_label > 0.5)[0].tolist()
    for c in fg_present:
        class_idx = c + 1
        cam_c     = cam_cls[class_idx]
        conf_mask = (cam_c > threshold).cpu().numpy()
        conf_t = torch.from_numpy(conf_mask.astype(np.float32)).to(feats_flat.device)
        cls_protos[class_idx] = mask_average_pool(feats_flat, conf_t)
        if conf_mask.sum() >= K:
            try:
                km     = KMeans(n_clusters=K, n_init=3, random_state=SEED)
                labels = km.fit_predict(feats_np[conf_mask])
                conf_indices = np.where(conf_mask)[0]
                for k in range(K):
                    k_indices = conf_indices[labels == k]
                    if len(k_indices) > 0:
                        k_mask = torch.zeros(HW, device=feats_flat.device)
                        k_mask[k_indices] = 1.0
                        cluster_protos[class_idx, k] = mask_average_pool(feats_flat, k_mask)
                        cluster_masks[:, class_idx, k] = k_mask
            except Exception:
                for k in range(K):
                    cluster_protos[class_idx, k] = cls_protos[class_idx]
        else:
            for k in range(K):
                cluster_protos[class_idx, k] = cls_protos[class_idx]
        present_classes.append(class_idx)

    # Detach: prototypes are only used for computing the transport plan
    # (assignment decisions). Gradients flow later through feature_activation
    # when prototypes are recomputed from live features.
    return cluster_protos.detach(), cls_protos.detach(), cluster_masks.detach(), present_classes


def cosine_similarity_matrix(A, B, eps=1e-8):
    A_norm = F.normalize(A.float(), dim=1, eps=eps)
    B_norm = F.normalize(B.float(), dim=1, eps=eps)
    return torch.mm(A_norm, B_norm.T)


def compute_similarity_aware_constraint(cluster_protos, cls_protos, present_classes):
    sims = []
    for c_idx in present_classes:
        p_cls   = cls_protos[c_idx].unsqueeze(0)
        p_clust = cluster_protos[c_idx]
        sim_ck  = cosine_similarity_matrix(p_clust, p_cls).squeeze(1)
        sims.append(sim_ck)
    X_flat = torch.cat(sims, dim=0)
    return F.softmax(X_flat, dim=0)


def sinkhorn_ot(S, x_constraint, reg=SINKHORN_REG, n_iter=SINKHORN_ITERS):
    M_cost = (1.0 - S).clamp(0, 2).float()
    K      = torch.exp(-M_cost / reg)
    u = torch.full((S.shape[0],), 1.0 / S.shape[0], device=S.device)
    v = x_constraint.to(S.device).float()
    a = torch.ones(S.shape[0], device=S.device)
    b = torch.ones(len(x_constraint), device=S.device)
    for _ in range(n_iter):
        a = u / (K @ b + 1e-9)
        b = v / (K.T @ a + 1e-9)
    return a.unsqueeze(1) * K * b.unsqueeze(0)


def feature_allocation(feats_flat, cluster_protos, cls_protos, present_classes):
    # Detach for allocation: T_star is used as fixed weights, gradients flow
    # through feature_activation instead. Avoids tracking 100 Sinkhorn iters.
    feats_T    = feats_flat.detach().T.float()
    proto_list = [cluster_protos[c_idx] for c_idx in present_classes]
    all_protos = torch.cat(proto_list, dim=0)
    S = cosine_similarity_matrix(feats_T, all_protos)
    x_constraint = compute_similarity_aware_constraint(
        cluster_protos, cls_protos, present_classes)
    T_star     = sinkhorn_ot(S, x_constraint)
    assignment = T_star.argmax(dim=1)
    return T_star, assignment, x_constraint


def feature_activation(feats_flat, cluster_protos, T_star, assignment,
                       present_classes, H, W, K=K_CLUSTERS):
    D, HW   = feats_flat.shape
    J1      = cluster_protos.shape[0]
    feats_T = feats_flat.T.float()
    updated_protos = cluster_protos.clone()
    proto_idx = 0
    for c_idx in present_classes:
        for k in range(K):
            assign_mask = (assignment == proto_idx).float()
            updated_protos[c_idx, k] = mask_average_pool(feats_flat, assign_mask)
            proto_idx += 1
    cam_proto_full = torch.zeros(J1, H, W, device=feats_flat.device)
    proto_idx = 0
    for c_idx in present_classes:
        cam_c_weighted = torch.zeros(HW, device=feats_flat.device)
        for k in range(K):
            p_ck   = updated_protos[c_idx, k].unsqueeze(0)
            sim_ck = cosine_similarity_matrix(feats_T, p_ck).squeeze(1)
            cam_ck = F.relu(sim_ck)
            t_ck   = T_star[:, proto_idx]
            cam_c_weighted += t_ck * cam_ck
            proto_idx += 1
        cam_proto_full[c_idx] = cam_c_weighted.reshape(H, W)
    return cam_proto_full, updated_protos


def binary_entropy(p, eps=1e-8):
    p = p.clamp(eps, 1 - eps)
    return -p * torch.log(p) - (1 - p) * torch.log(1 - p)


def ot_consistency_loss(cam_proto, cam_cls, T_star, img_label,
                        present_classes, K=K_CLUSTERS):
    HW     = cam_proto.shape[1]
    J1     = cam_proto.shape[0]
    C      = J1 - 1
    log_C1 = np.log(C + 1) + 1e-8
    cam_proto_f = cam_proto.float()
    cam_cls_f   = cam_cls.float()
    total_loss = torch.tensor(0.0, device=cam_proto.device)
    proto_idx  = 0
    count      = 0
    for c_idx in present_classes:
        t_ic = T_star[:, proto_idx:proto_idx+K].sum(dim=1)
        proto_idx += K
        H_t  = binary_entropy(t_ic)
        l_c  = 1.0 if c_idx == 0 else float(img_label[c_idx - 1].item())
        w_ic = (l_c * (1.0 - H_t / log_C1)).clamp(0)
        # Per-class max normalization to [0,1] then L1 distance (Eq. 12)
        cp = cam_proto_f[c_idx]
        cc = cam_cls_f[c_idx]
        cp = cp / (cp.max() + 1e-8)
        cc = cc / (cc.max() + 1e-8)
        diff = (cp - cc).abs()
        total_loss = total_loss + (w_ic * diff).sum() / (HW + 1e-8)
        count += 1
    return total_loss / max(count, 1)


def classification_loss(logits, img_labels):
    return F.multilabel_soft_margin_loss(logits, img_labels)


def pot_forward_single(feats, cam_cls, img_label, H, W):
    D = feats.shape[0]
    feats_flat = feats.reshape(D, -1)
    cam_flat   = cam_cls.reshape(cam_cls.shape[0], -1)
    cluster_protos, cls_protos, _, present_classes = feature_partitioning(
        feats_flat, cam_flat, img_label)
    T_star, assignment, _ = feature_allocation(
        feats_flat, cluster_protos, cls_protos, present_classes)
    cam_proto_full, _ = feature_activation(
        feats_flat, cluster_protos, T_star, assignment, present_classes, H, W)
    cam_proto_flat = cam_proto_full.reshape(cam_proto_full.shape[0], -1)
    loss_otcon = ot_consistency_loss(
        cam_proto_flat, cam_flat, T_star, img_label, present_classes)
    return cam_proto_full, loss_otcon


# TODO: The full POT pipeline (Section 4.2) generates pseudo-labels using
# DenseCRF + IRN on prototype CAMs, then trains DeepLab-v2 on those labels.
# This implementation uses argmax on CAMs directly as a simplification.
def cam_to_segmentation(cam_proto, threshold=0.3):
    cam_norm = cam_proto.clone()
    for c in range(cam_norm.shape[0]):
        mx = cam_norm[c].max()
        if mx > 0:
            cam_norm[c] /= mx
    seg_map = cam_norm.argmax(dim=0)
    max_act = cam_norm.max(dim=0)[0]
    seg_map[max_act < threshold] = 0
    return seg_map


# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 5 — Entrenamiento y Evaluación
# ═════════════════════════════════════════════════════════════════════════════

def polynomial_lr(step, total_steps, power=0.9, base_lr=LR_ENCODER):
    factor = max(0.0, 1 - step / total_steps)
    return float(base_lr * (factor ** power))


def train_one_epoch(model, train_loader, optimizer, epoch, global_step,
                    total_steps, device):
    model.train()
    total_loss_cls   = 0.0
    total_loss_otcon = 0.0
    n_batches        = len(train_loader)

    for batch_idx, (images, img_labels, _) in enumerate(train_loader):
        images     = images.to(device)
        img_labels = img_labels.to(device)

        lr_enc = float(polynomial_lr(global_step, total_steps))
        lr_ext = float(lr_enc * (LR_EXTRA / LR_ENCODER))
        optimizer.param_groups[0]['lr'] = lr_enc
        optimizer.param_groups[1]['lr'] = lr_ext

        logits, cam_cls, feats, _ = model(images)
        loss_cls = classification_loss(logits, img_labels)

        B, _, H, W = feats.shape
        batch_loss_otcon = torch.tensor(0.0, device=device)
        for b in range(B):
            try:
                _, loss_otcon_b = pot_forward_single(
                    feats[b], cam_cls[b], img_labels[b], H, W)
                batch_loss_otcon = batch_loss_otcon + loss_otcon_b
            except Exception as e:
                if batch_idx == 0 and b == 0:
                    print(f'   [WARN] POT forward failed: {e}')
        batch_loss_otcon = batch_loss_otcon / B

        loss_total = loss_cls + THETA * batch_loss_otcon
        optimizer.zero_grad()
        loss_total.backward()
        nn.utils.clip_grad_norm_(model.parameters(), max_norm=10.0)
        optimizer.step()
        global_step += 1

        total_loss_cls   += loss_cls.item()
        total_loss_otcon += batch_loss_otcon.item()

        if batch_idx % 50 == 0:
            print(f'   Epoch {epoch+1} [{batch_idx}/{n_batches}] '
                  f'L_cls={loss_cls.item():.4f} '
                  f'L_otcon={batch_loss_otcon.item():.4f} '
                  f'L_total={loss_total.item():.4f} '
                  f'LR={lr_enc:.6f}')

    avg_cls   = total_loss_cls   / n_batches
    avg_otcon = total_loss_otcon / n_batches
    avg_total = avg_cls + THETA * avg_otcon
    return avg_cls, avg_otcon, avg_total, global_step


def evaluate(model, loader, num_classes, device, n_samples=None):
    model.eval()
    intersection  = np.zeros(num_classes)
    union         = np.zeros(num_classes)
    dice_num      = np.zeros(num_classes)
    dice_den      = np.zeros(num_classes)
    total_correct = 0
    total_pixels  = 0
    processed     = 0

    with torch.no_grad():
        for images, img_labels, masks_gt in loader:
            images     = images.to(device)
            img_labels = img_labels.to(device)
            logits, cam_cls, feats, _ = model(images)
            B, _, H, W = feats.shape

            for b in range(B):
                mask_gt = masks_gt[b].numpy()
                try:
                    cam_proto, _ = pot_forward_single(
                        feats[b], cam_cls[b], img_labels[b], H, W)
                    cam_up = F.interpolate(
                        cam_proto.unsqueeze(0), size=mask_gt.shape,
                        mode='bilinear', align_corners=False).squeeze(0)
                    seg_pred = cam_to_segmentation(cam_up).cpu().numpy()
                    seg_fg   = seg_pred - 1
                except Exception:
                    seg_fg = np.full(mask_gt.shape, -1, dtype=np.int64)

                valid      = (mask_gt != 255)
                pred_valid = seg_fg[valid]
                gt_valid   = mask_gt[valid]
                total_correct += (pred_valid == gt_valid).sum()
                total_pixels  += valid.sum()

                for c in range(num_classes):
                    pred_c = (pred_valid == c)
                    gt_c   = (gt_valid == c)
                    inter  = (pred_c & gt_c).sum()
                    uni    = (pred_c | gt_c).sum()
                    intersection[c] += inter
                    union[c]        += uni
                    dice_num[c]     += 2 * inter
                    dice_den[c]     += pred_c.sum() + gt_c.sum()
                processed += 1

            if n_samples and processed >= n_samples:
                break

    iou_per_class  = np.where(union > 0, intersection / union, np.nan)
    dice_per_class = np.where(dice_den > 0, dice_num / dice_den, np.nan)
    return {
        'mIoU':           float(np.nanmean(iou_per_class)),
        'Dice':           float(np.nanmean(dice_per_class)),
        'PixelAcc':       float(total_correct / max(total_pixels, 1)),
        'iou_per_class':  iou_per_class.tolist(),
        'dice_per_class': dice_per_class.tolist(),
        'n_samples':      processed
    }


# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 6 — Ablation Study
# ═════════════════════════════════════════════════════════════════════════════

def evaluate_ablation(model, val_loader, num_classes, device,
                      use_multi_cluster=True, use_ot=True,
                      use_similarity_constraint=True, n_samples=100):
    model.eval()
    intersection = np.zeros(num_classes)
    union        = np.zeros(num_classes)
    processed    = 0
    K_use        = K_CLUSTERS if use_multi_cluster else 1

    with torch.no_grad():
        for images, img_labels, masks_gt in val_loader:
            images     = images.to(device)
            img_labels = img_labels.to(device)
            logits, cam_cls, feats, _ = model(images)
            B, _, H, W = feats.shape

            for b in range(B):
                mask_gt = masks_gt[b].numpy()
                try:
                    feats_flat = feats[b].reshape(feats[b].shape[0], -1)
                    cam_flat   = cam_cls[b].reshape(cam_cls[b].shape[0], -1)
                    cluster_protos, cls_protos, _, present = feature_partitioning(
                        feats_flat, cam_flat, img_labels[b], K=K_use)

                    if use_multi_cluster and len(present) > 0:
                        if use_ot:
                            if use_similarity_constraint:
                                # Full POT: similarity-aware OT
                                T_star, assignment, _ = feature_allocation(
                                    feats_flat, cluster_protos, cls_protos, present)
                            else:
                                # Vanilla OT: uniform constraints
                                N = len(present) * K_use
                                x_unif = torch.full((N,), 1.0/N, device=device)
                                proto_list = [cluster_protos[c] for c in present]
                                all_p = torch.cat(proto_list, dim=0)
                                S = cosine_similarity_matrix(feats_flat.T.float(), all_p)
                                T_star = sinkhorn_ot(S, x_unif)
                                assignment = T_star.argmax(dim=1)
                        else:
                            # No OT: assign by nearest prototype (cosine similarity)
                            proto_list = [cluster_protos[c] for c in present]
                            all_p = torch.cat(proto_list, dim=0)
                            S = cosine_similarity_matrix(feats_flat.T.float(), all_p)
                            assignment = S.argmax(dim=1)
                            # Build uniform T_star for feature_activation
                            N = len(present) * K_use
                            T_star = torch.zeros(feats_flat.shape[1], N, device=device)
                            for i in range(feats_flat.shape[1]):
                                T_star[i, assignment[i]] = 1.0 / feats_flat.shape[1]

                        cam_proto, _ = feature_activation(
                            feats_flat, cluster_protos, T_star, assignment,
                            present, H, W, K=K_use)
                    else:
                        cam_proto = cam_cls[b]

                    cam_up   = F.interpolate(cam_proto.unsqueeze(0),
                                            size=mask_gt.shape,
                                            mode='bilinear',
                                            align_corners=False).squeeze(0)
                    seg_pred = cam_to_segmentation(cam_up).cpu().numpy() - 1
                    seg_pred = np.clip(seg_pred, 0, num_classes - 1)
                except Exception:
                    seg_pred = np.zeros(mask_gt.shape, dtype=np.int64)

                valid = (mask_gt != 255)
                for c in range(num_classes):
                    pc = (seg_pred[valid] == c)
                    gc = (mask_gt[valid] == c)
                    intersection[c] += (pc & gc).sum()
                    union[c]        += (pc | gc).sum()
                processed += 1
            if processed >= n_samples:
                break

    iou = np.where(union > 0, intersection / union, np.nan)
    return float(np.nanmean(iou))


# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 7 — Experimento Individual
# ═════════════════════════════════════════════════════════════════════════════

def run_experiment(dataset_name, data_root, num_classes, img_size,
                   subset_size, batch_size, num_epochs, num_workers, device,
                   output_dir):
    """Ejecuta un experimento completo del grid search."""

    subset_str = str(subset_size) if subset_size else 'full'
    exp_name   = f'{dataset_name}_img{img_size}_subset{subset_str}'
    print(f'\n{"="*70}')
    print(f'  EXPERIMENTO: {exp_name}')
    print(f'  Dataset={dataset_name} | IMG_SIZE={img_size} | '
          f'SUBSET={subset_str} | Epochs={num_epochs}')
    print(f'{"="*70}')
    t_start = time.time()

    # ── Transformaciones ─────────────────────────────────────────────────────
    train_tf = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])
    val_tf = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ])

    # ── Datasets ─────────────────────────────────────────────────────────────
    if dataset_name == 'cityscapes':
        train_ds = CityscapesWeakDataset(data_root, 'train', train_tf, img_size)
        val_ds   = CityscapesWeakDataset(data_root, 'val',   val_tf,   img_size)
    elif dataset_name == 'mapillary_vistas_v2':
        train_ds = MapillaryWeakDataset(data_root, 'training',   train_tf, img_size, num_classes)
        val_ds   = MapillaryWeakDataset(data_root, 'validation', val_tf,   img_size, num_classes)
    else:
        train_ds = COCOWeakDataset(data_root, 'train', train_tf, img_size, num_classes)
        val_ds   = COCOWeakDataset(data_root, 'val',   val_tf,   img_size, num_classes)

    if subset_size is not None:
        train_ds = Subset(train_ds, range(min(subset_size, len(train_ds))))
        print(f'  Subset de entrenamiento: {len(train_ds)} imágenes')

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True,
                              num_workers=num_workers, pin_memory=True,
                              drop_last=True)
    val_loader   = DataLoader(val_ds,   batch_size=batch_size, shuffle=False,
                              num_workers=num_workers, pin_memory=True)

    # ── Modelo ───────────────────────────────────────────────────────────────
    model = POTEncoder(num_classes=num_classes, feat_dim=FEAT_DIM).to(device)
    encoder_params = (list(model.layer0.parameters()) +
                      list(model.layer1.parameters()) +
                      list(model.layer2.parameters()) +
                      list(model.layer3.parameters()) +
                      list(model.layer4.parameters()))
    extra_params = (list(model.hier_proj.parameters()) +
                    list(model.classifier.parameters()))

    total_p = sum(p.numel() for p in model.parameters()) / 1e6
    print(f'  Modelo: {total_p:.1f}M parámetros')

    optimizer = torch.optim.SGD([
        {'params': encoder_params, 'lr': LR_ENCODER},
        {'params': extra_params,   'lr': LR_EXTRA}
    ], momentum=0.9, weight_decay=1e-4)

    total_steps = num_epochs * len(train_loader)
    global_step = 0

    # ── Training loop ────────────────────────────────────────────────────────
    history = {
        'train_loss_cls': [], 'train_loss_otcon': [], 'train_loss_total': [],
        'val_miou': [], 'val_dice': [], 'val_pixel_acc': []
    }
    best_miou = 0.0

    for epoch in range(num_epochs):
        t_ep = time.time()
        avg_cls, avg_otcon, avg_total, global_step = train_one_epoch(
            model, train_loader, optimizer, epoch, global_step,
            total_steps, device)
        history['train_loss_cls'].append(avg_cls)
        history['train_loss_otcon'].append(avg_otcon)
        history['train_loss_total'].append(avg_total)

        metrics = evaluate(model, val_loader, num_classes, device, n_samples=200)
        history['val_miou'].append(metrics['mIoU'])
        history['val_dice'].append(metrics['Dice'])
        history['val_pixel_acc'].append(metrics['PixelAcc'])

        if metrics['mIoU'] > best_miou:
            best_miou = metrics['mIoU']

        elapsed_ep = time.time() - t_ep
        print(f'  [Epoch {epoch+1}/{num_epochs}] '
              f'L_cls={avg_cls:.4f} L_otcon={avg_otcon:.4f} '
              f'mIoU={metrics["mIoU"]:.4f} Dice={metrics["Dice"]:.4f} '
              f'PixAcc={metrics["PixelAcc"]:.4f} '
              f'({elapsed_ep/60:.1f} min)')

    # ── Evaluación final (val completo) ──────────────────────────────────────
    print(f'  Evaluación final completa...')
    final_metrics = evaluate(model, val_loader, num_classes, device)

    elapsed_total = time.time() - t_start
    print(f'  RESULTADO FINAL [{exp_name}]: '
          f'mIoU={final_metrics["mIoU"]:.4f} | '
          f'Dice={final_metrics["Dice"]:.4f} | '
          f'PixAcc={final_metrics["PixelAcc"]:.4f} | '
          f'Tiempo={elapsed_total/60:.1f} min')

    # ── Guardar resultado individual ─────────────────────────────────────────
    result = {
        'experiment': exp_name,
        'dataset': dataset_name,
        'img_size': img_size,
        'subset_size': subset_size,
        'num_epochs': num_epochs,
        'batch_size': batch_size,
        'best_miou': best_miou,
        'mIoU': final_metrics['mIoU'],
        'Dice': final_metrics['Dice'],
        'PixelAcc': final_metrics['PixelAcc'],
        'iou_per_class': final_metrics['iou_per_class'],
        'dice_per_class': final_metrics['dice_per_class'],
        'n_val_samples': final_metrics['n_samples'],
        'history': history,
        'elapsed_minutes': elapsed_total / 60.0,
        'hyperparams': {
            'K_clusters': K_CLUSTERS, 'cam_threshold': CAM_THRESHOLD,
            'theta': THETA, 'lr_encoder': LR_ENCODER, 'lr_extra': LR_EXTRA,
            'sinkhorn_reg': SINKHORN_REG, 'sinkhorn_iters': SINKHORN_ITERS
        }
    }

    result_path = os.path.join(output_dir, f'results_{exp_name}.json')
    with open(result_path, 'w') as f:
        json.dump(result, f, indent=2)
    print(f'  Guardado: {result_path}')

    return result, model, val_loader


# ═════════════════════════════════════════════════════════════════════════════
# SECCIÓN 8 — Main: Grid Search + Ablation
# ═════════════════════════════════════════════════════════════════════════════

def main():
    args   = parse_args()
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f'Dispositivo: {device}')
    if torch.cuda.is_available():
        print(f'GPU: {torch.cuda.get_device_name(0)}')
        print(f'VRAM: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB')

    # ── Config por dataset ───────────────────────────────────────────────────
    if args.dataset == 'cityscapes':
        num_classes  = 19
        class_names  = CITYSCAPES_CLASSES
        data_root    = os.path.join(args.base_dir, 'cityscapes')
    elif args.dataset == 'mapillary_vistas_v2':
        data_root    = os.path.join(args.base_dir, 'mapillary_vistas_v2')
        config_path  = os.path.join(data_root, 'config_v2.0.json')
        print(f'Leyendo configuración de: {config_path}')
        with open(config_path, 'r') as f:
            cfg = json.load(f)
        num_classes  = len(cfg['labels'])
        class_names  = [l['readable'] for l in cfg['labels']]
    else:
        num_classes  = 80
        class_names  = COCO_CLASSES
        data_root    = os.path.join(args.base_dir, 'coco_dataset')

    output_dir = os.path.join(args.output_dir, args.dataset)
    os.makedirs(output_dir, exist_ok=True)
    print(f'Dataset: {args.dataset} ({num_classes} clases)')
    print(f'Data root: {data_root}')
    print(f'Output dir: {output_dir}')

    # ── Grid search ──────────────────────────────────────────────────────────
    grid_img_sizes    = [224, 336, 448]
    grid_subset_sizes = [500, 1000, 1500]

    all_results = []
    best_result = None
    best_model  = None
    best_val_loader = None

    for img_size, subset_size in itertools.product(grid_img_sizes, grid_subset_sizes):
        result, model, val_loader = run_experiment(
            dataset_name=args.dataset,
            data_root=data_root,
            num_classes=num_classes,
            img_size=img_size,
            subset_size=subset_size,
            batch_size=args.batch_size,
            num_epochs=args.epochs,
            num_workers=args.num_workers,
            device=device,
            output_dir=output_dir
        )
        all_results.append(result)

        # Track best
        if best_result is None or result['mIoU'] > best_result['mIoU']:
            best_result     = result
            best_model      = model
            best_val_loader = val_loader

        # ── Guardar CSV parcial ──────────────────────────────────────────────
        csv_path = os.path.join(output_dir, f'grid_search_{args.dataset}.csv')
        with open(csv_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'experiment', 'img_size', 'subset_size',
                'mIoU', 'Dice', 'PixelAcc', 'elapsed_minutes'])
            writer.writeheader()
            for r in all_results:
                writer.writerow({
                    'experiment':      r['experiment'],
                    'img_size':        r['img_size'],
                    'subset_size':     r['subset_size'] or 'full',
                    'mIoU':            f'{r["mIoU"]:.6f}',
                    'Dice':            f'{r["Dice"]:.6f}',
                    'PixelAcc':        f'{r["PixelAcc"]:.6f}',
                    'elapsed_minutes': f'{r["elapsed_minutes"]:.1f}'
                })
        print(f'  CSV parcial guardado: {csv_path}')

    # ── Resumen del grid search ──────────────────────────────────────────────
    print(f'\n{"="*70}')
    print(f'  RESUMEN GRID SEARCH — {args.dataset.upper()}')
    print(f'{"="*70}')
    print(f'  {"Experimento":<40} {"mIoU":>8} {"Dice":>8} {"PixAcc":>8} {"Tiempo":>8}')
    print(f'  {"-"*66}')
    for r in sorted(all_results, key=lambda x: x['mIoU'], reverse=True):
        print(f'  {r["experiment"]:<40} '
              f'{r["mIoU"]*100:>7.2f}% '
              f'{r["Dice"]*100:>7.2f}% '
              f'{r["PixelAcc"]*100:>7.2f}% '
              f'{r["elapsed_minutes"]:>6.1f}m')

    print(f'\n  Mejor: {best_result["experiment"]} — '
          f'mIoU={best_result["mIoU"]*100:.2f}%')

    # ── Ablation Study (sobre el mejor modelo) ──────────────────────────────
    print(f'\n{"="*70}')
    print(f'  ABLATION STUDY — {args.dataset.upper()} '
          f'(config: {best_result["experiment"]})')
    print(f'{"="*70}')

    # NOTE: This ablation evaluates different inference pipelines on the same
    # trained model. A rigorous ablation would train separate models per
    # condition (Tab. 3-4 in the paper). This is a known simplification.
    #                                (multi_cluster, use_ot, similarity_constraint)
    ablation_configs = [
        ('I   — Baseline (single-cluster)',         False, False, False),
        ('II  — Multi-cluster, sin OT',             True,  False, False),
        ('III — Multi-cluster + OT uniforme',       True,  True,  False),
        ('IV  — POT completo (SOT + L_otcon)',      True,  True,  True),
    ]

    ablation_results = {}
    for name, mc, use_ot, sim_constr in ablation_configs:
        print(f'   Evaluando: {name} ...')
        miou = evaluate_ablation(best_model, best_val_loader, num_classes,
                                 device, mc, use_ot, sim_constr, n_samples=100)
        ablation_results[name] = miou
        print(f'   → mIoU = {miou*100:.2f}%')

    print(f'\n  {"Configuración":<40} {"mIoU":>8}')
    print(f'  {"-"*50}')
    for name, miou in ablation_results.items():
        print(f'  {name:<40} {miou*100:>7.2f}%')

    # Guardar ablation
    abl_path = os.path.join(output_dir, f'ablation_{args.dataset}.json')
    with open(abl_path, 'w') as f:
        json.dump({
            'best_config': best_result['experiment'],
            'results': {k: v for k, v in ablation_results.items()}
        }, f, indent=2)
    print(f'  Ablation guardado: {abl_path}')

    # ── Reporte final por clase ──────────────────────────────────────────────
    print(f'\n{"="*70}')
    print(f'  IoU POR CLASE — Mejor modelo: {best_result["experiment"]}')
    print(f'{"="*70}')
    iou_cls = best_result['iou_per_class']
    print(f'  {"Clase":<25} {"IoU":>8}')
    print(f'  {"-"*35}')
    for i, cls_name in enumerate(class_names):
        if i < len(iou_cls) and not np.isnan(iou_cls[i]):
            print(f'  {cls_name:<25} {iou_cls[i]*100:>7.2f}%')
        else:
            print(f'  {cls_name:<25} {"N/A":>8}')

    print(f'\n  Proceso completo. Resultados en: {output_dir}')


if __name__ == '__main__':
    main()