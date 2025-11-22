import os
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import torch
import torch.optim as optim
from sklearn.metrics import confusion_matrix
from torch import nn
from torch.cuda.amp import GradScaler, autocast
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from torchvision.models import VGG16_Weights

# Download latest version
path = "datasets/msambare/fer2013/versions/1"

data_root = Path(path)
train_dir = data_root / "train"
test_dir = data_root / "test"

print("Train dir:", train_dir, "->", train_dir.exists())
print("Test dir :", test_dir, "->", test_dir.exists())

print("\nClases en train:")
print([d.name for d in train_dir.iterdir() if d.is_dir()])

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Usando dispositivo:", device)

# Transforms para el conjunto de entrenamiento
train_transform = transforms.Compose(
    [
        transforms.Grayscale(num_output_channels=3),  # Asegura 3 canales
        transforms.Resize((224, 224)),  # Tamaño que usa VGG16
        transforms.RandomHorizontalFlip(p=0.5),  # Voltear horizontalmente (espejo)
        transforms.RandomRotation(degrees=5),  # Rotar levemente +/- 15 grados
        transforms.ColorJitter(brightness=0.2, contrast=0.2),  # Variar luz
        transforms.ToTensor(),  # [0,255] -> [0,1] tensor
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],  # ImageNet
            std=[0.229, 0.224, 0.225],
        ),
    ]
)

# Transforms para el conjunto de prueba (sin augmentación)
test_transform = transforms.Compose(
    [
        transforms.Grayscale(num_output_channels=3),
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ]
)


train_dataset = datasets.ImageFolder(root=str(train_dir), transform=train_transform)
test_dataset = datasets.ImageFolder(root=str(test_dir), transform=test_transform)

print("Número de imágenes en train:", len(train_dataset))
print("Número de imágenes en test :", len(test_dataset))
print("Clases (orden de índices):", train_dataset.classes)

batch_size = 64

train_loader = DataLoader(
    train_dataset,
    batch_size=batch_size,
    shuffle=True,  # Mezcla los ejemplos en cada época
    num_workers=4,
    pin_memory=True,
)

test_loader = DataLoader(
    test_dataset,
    batch_size=batch_size,
    shuffle=False,  # En test no hace falta mezclar
    num_workers=4,
    pin_memory=True,
)

print("Batches en train_loader:", len(train_loader))
print("Batches en test_loader :", len(test_loader))

images, labels = next(iter(train_loader))
print("Shape del batch de imágenes:", images.shape)
print("Shape del batch de labels  :", labels.shape)

# 1. Cargar el modelo VGG16 sin pesos pre-entrenados
model = models.vgg16(weights=None)

# 2. Cargar los pesos manualmente desde el archivo local
weights_path = "vgg16_imagenet.pth"
model.load_state_dict(torch.load(weights_path))

# 3. Enviar el modelo al dispositivo que definimos antes
model = model.to(device)

print(type(model))

print(model.classifier)


# Número de clases en nuestro problema
num_classes = 7

# Obtener cuántas entradas tiene la última capa
in_features = model.classifier[6].in_features
print("in_features de la última capa:", in_features)

# Reemplazar la última capa por una nueva: 4096 -> 7
model.classifier[6] = nn.Linear(in_features, num_classes)

# Enviar de nuevo la parte modificada al device
model = model.to(device)

print(model.classifier)

# Congelar TODAS las capas convolucionales (features)
for param in model.features.parameters():
    param.requires_grad = False

# Función de pérdida para clasificación multiclase
criterion = nn.CrossEntropyLoss()

# Solo entrenamos los parámetros con requires_grad=True
trainable_params = [p for p in model.parameters() if p.requires_grad]

print("Número de parámetros entrenables:", sum(p.numel() for p in trainable_params))

# Optimizador
optimizer = optim.Adam(trainable_params, lr=1e-4, weight_decay=1e-4)

# Inicializar el GradScaler para AMP
scaler = GradScaler()

num_epochs = 10

for epoch in range(num_epochs):
    model.train()  # pone el modelo en modo entrenamiento

    running_loss = 0.0
    correct = 0
    total = 0

    for images, labels in train_loader:
        # Enviar batch a CPU/GPU
        images = images.to(device)
        labels = labels.to(device)

        # 1. Resetear gradientes acumulados
        optimizer.zero_grad()

        # 2. Forward pass con autocast
        with autocast():
            outputs = model(images)  # shape: [batch, 7]
            loss = criterion(outputs, labels)

        # 3. Backpropagation escalada
        scaler.scale(loss).backward()

        # 4. Actualizar pesos (desescala gradientes)
        scaler.step(optimizer)

        # 5. Actualizar el scaler para la siguiente iteración
        scaler.update()

        # Acumular estadísticas de entrenamiento
        running_loss += loss.item() * images.size(0)

        # Predicciones: índice de la clase con mayor logit
        _, predicted = torch.max(outputs, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

    epoch_loss = running_loss / total
    epoch_acc = correct / total

    # Evaluacion en test
    model.eval()  # modo evaluación (sin dropout, etc.)
    test_correct = 0
    test_total = 0

    with torch.no_grad():  # sin gradientes
        for images, labels in test_loader:
            images = images.to(device)
            labels = labels.to(device)

            with autocast():
                outputs = model(images)
            _, predicted = torch.max(outputs, 1)

            test_total += labels.size(0)
            test_correct += (predicted == labels).sum().item()

    test_acc = test_correct / test_total

    print(
        f"Época [{epoch + 1}/{num_epochs}] "
        f"- Train Loss: {epoch_loss:.4f} "
        f"- Train Acc: {epoch_acc:.4f} "
        f"- Test Acc: {test_acc:.4f}"
    )

model.eval()

all_preds = []
all_labels = []

with torch.no_grad():
    for images, labels in test_loader:
        images = images.to(device)
        labels = labels.to(device)

        with autocast():
            outputs = model(images)
        _, predicted = torch.max(outputs, 1)

        all_preds.append(predicted.cpu())
        all_labels.append(labels.cpu())

all_preds = torch.cat(all_preds)
all_labels = torch.cat(all_labels)

test_acc = (all_preds == all_labels).float().mean().item()
print(f"Accuracy final en test: {test_acc:.4f}")

# 1. Clases y número de clases
classes = train_dataset.classes
num_classes = len(classes)
print("Clases (orden):", classes)

# 2. Matriz de confusión (filas: real, columnas: predicho)
cm = confusion_matrix(all_labels, all_preds)
print("Shape cm:", cm.shape)

# 3. Normalizar por fila
cm_norm = cm.astype("float") / cm.sum(axis=1, keepdims=True)

fig, ax = plt.subplots(figsize=(8, 6))

im = ax.imshow(cm_norm, interpolation="nearest", cmap=plt.cm.Blues)
cbar = plt.colorbar(im, ax=ax)
cbar.ax.set_ylabel("Proporción", rotation=270, labelpad=15)

# 4. Ticks y etiquetas
ax.set_xticks(np.arange(num_classes))
ax.set_yticks(np.arange(num_classes))
ax.set_xticklabels(classes, rotation=45, ha="right")
ax.set_yticklabels(classes)

ax.set_xlabel("Predicción")
ax.set_ylabel("Etiqueta real")
ax.set_title("Matriz de confusión normalizada (FER-2013, VGG16)")

# 5. Escribir los valores dentro de cada celda
thresh = cm_norm.max() / 2.0
for i in range(num_classes):
    for j in range(num_classes):
        value = cm_norm[i, j]
        text_color = "white" if value > thresh else "black"
        ax.text(
            j, i, f"{value:.2f}", ha="center", va="center", color=text_color, fontsize=9
        )

plt.tight_layout()
plt.savefig("confusion_matrix.png")
plt.show()

torch.save(model.state_dict(), "vgg16_fer2013.pth")
print("Modelo guardado en vgg16_fer2013.pth")
