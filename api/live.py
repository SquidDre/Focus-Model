import cv2
import torch
import torchvision.transforms as transforms
from PIL import Image
import torch.nn as nn
import torch.nn.functional as F
import fastapi as FastAPI
from pydantic import BaseModel

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
device = torch.device("cpu") # Laptops usually run inference just fine on CPU!
model = FocusStateCNN().to(device)
model.load_state_dict(torch.load('focus_model.pth', map_location=device))
model.eval() # Turn off learning mode

# 3. Setup the Image Formatter (No augmentation here, just resizing!)
transform = transforms.Compose([
    transforms.Resize((64, 64)),
    transforms.ToTensor()
])

classes = ['Distracted', 'Focused']

class ImageData(BaseModel):
    image_b64: str #frontend sends

# 4. Boot up the Webcam (0 is usually the default built-in laptop camera)
cap = cv2.VideoCapture(0)

print("🎥 Starting live focus tracker... Press 'q' to quit.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame.")
        break

    # OpenCV pulls images in BGR format, but our model learned on standard RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    pil_img = Image.fromarray(rgb_frame)

    # Format for the model: [1, 3, 64, 64]
    input_tensor = transform(pil_img).unsqueeze(0).to(device)

    # 5. Make the Prediction
    with torch.no_grad():
        output = model(input_tensor)
        _, predicted_index = torch.max(output, 1)
        status = classes[predicted_index.item()]

    # 6. Draw the prediction on the screen
    # Green text for Focused, Red text for Distracted
    color = (0, 255, 0) if status == 'Focused' else (0, 0, 255) 
    cv2.putText(frame, f"State: {status}", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

    # Show the video window
    cv2.imshow("Live Focus Tracker", frame)

    # Listen for the 'q' key to quit the loop
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()