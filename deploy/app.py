import streamlit as st
import torch
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import joblib
import io

st.set_page_config(
    layout="wide",
    page_title="Crop Classifier App",
    page_icon="🌿"
)

try:
    model_data = joblib.load("crop_classifier_model.pkl")
    model = models.resnet18(pretrained=False)
    model.fc = torch.nn.Linear(model.fc.in_features, len(model_data["class_to_idx"]))
    model.load_state_dict(model_data["model_state_dict"])
    model.eval()

    idx_to_class = {v: k for k, v in model_data["class_to_idx"].items()}

except KeyError as e:
    st.error(f"Error loading model data: Key {e} not found. Please check your pickled file.")
    st.stop()
except FileNotFoundError:
    st.error("Model file 'crop_classifier_model.pkl' not found. Please ensure it is in the same directory.")
    st.stop()


transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406],
                         [0.229, 0.224, 0.225])
])

st.title("🌱 Crop Classifier")
st.markdown("Upload an image of a crop and our model will predict what it is.")

uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("Your Uploaded Image")
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, use_container_width=True)

    with col2:
        st.subheader("Prediction Result")
        with st.spinner('Analyzing the image...'):
            input_tensor = transform(image).unsqueeze(0)

            with torch.no_grad():
                output = model(input_tensor)
                _, predicted = torch.max(output, 1)

            class_name = idx_to_class[predicted.item()]
        
        st.success(f"**Predicted Crop:**")
        st.subheader(f"{class_name.upper()} 🌱")