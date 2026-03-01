import cv2
import torch
import torchvision.transforms as transforms
from PIL import Image
import torch.nn as nn
import torch.nn.functional as F
import fastapi as FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware # Added for React connectivity
import base64
import io

# Blueprint
class FocusStateCNN(nn.Module):
    def __init__(self):
        super(FocusStateCNN, self).__init__()
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=16, kernel_size=3, padding=1)
        self.pool = nn.MaxPool2d(kernel_size=2, stride=2)
        self.fc1 = nn.Linear(16 * 32 * 32, 2) 

    def forward(self, x):
        x = self.pool(F.relu(self.conv1(x)))
        x = x.view(-1, 16 * 32 * 32)
        x = self.fc1(x)
        return x

app = FastAPI.FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for simplicity (adjust in production)
    allow_methods=["*"],
    allow_headers=["*"],
)

device = torch.device("cpu") # Laptops usually run inference just fine on CPU!
model = FocusStateCNN().to(device)
model.load_state_dict(torch.load('focus_model.pth', map_location=device))
model.eval() # Turn off learning mode

# 3. Setup the Image Formatter (No augmentation here, just resizing!)
transform = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor()
])

classes = ['Focused', 'Distracted'] # Swapped order to match training labels

class ImageData(BaseModel):
    image_b64: str #frontend sends

@app.post("/predict-focus")
async def predict_focus(data: ImageData):
    if "," in data.image_b64:
            header, encoded = data.image_b64.split(",", 1)
    else:
            encoded = data.image_b64

            
    image_bytes = base64.b64decode(encoded)
    pil_img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # b. Transform and Predict
    input_tensor = transform(pil_img).unsqueeze(0).to(device)
    
    with torch.no_grad():
        output = model(input_tensor)
        _, predicted_index = torch.max(output, 1)
        status = classes[predicted_index.item()]

    return {"status": status}