import streamlit as st
from ultralytics import YOLO
import cv2
import tempfile
from PIL import Image
import numpy as np

st.set_page_config(page_title="Traffic AI: Image & Video", layout="wide")
st.title("🚗 Traffic Object Detection (Images & Video)")

# تحميل الموديل
@st.cache_resource
def load_model():
    return YOLO('my_best_model.pt')

model = load_model()

# القائمة الجانبية
st.sidebar.header("Settings")
source_radio = st.sidebar.radio("Select Source", ["Image", "Video"])
conf_threshold = st.sidebar.slider("Confidence", 0.0, 1.0, 0.45)

# --- قسم الصور (عرض مقارنة) ---
if source_radio == "Image":
    uploaded_file = st.file_uploader("Upload Image", type=['jpg', 'jpeg', 'png'])
    if uploaded_file:
        image = Image.open(uploaded_file)
        
        # إنشاء عمودين بنسبة متساوية
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Original Image")
            st.image(image, use_container_width=True)
            
        with col2:
            st.subheader("AI Detection")
            # تشغيل الموديل
            results = model.predict(source=np.array(image), conf=conf_threshold)
            res_plotted = results[0].plot()
            # عرض الصورة بعد الرسم عليها
            st.image(res_plotted, use_container_width=True)
            
        st.success(f"Successfully detected objects with {conf_threshold*100}% confidence!")
# --- قسم الفيديو ---
else:
    uploaded_video = st.file_uploader("Upload Video", type=['mp4', 'mov', 'avi'])
    if uploaded_video:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_video.read())
        
        vid_cap = cv2.VideoCapture(tfile.name)
        st_frame = st.empty()
        
        frame_count = 0 # عداد الفريمات
        
        while vid_cap.isOpened():
            success, frame = vid_cap.read()
            if success:
                frame_count += 1
                
                # تخطي الفريمات: هيعالج الفريمات الزوجية فقط (بيوفر 50% من المجهود)
                if frame_count % 2 != 0:
                    continue
                
                # تقليل حجم الفريم قبل المعالجة لتسريع الحسابات (imgsz=320)
                results = model.predict(frame, conf=conf_threshold, imgsz=320, verbose=False)
                
                res_plotted = results[0].plot()
                
                # عرض الفريم المعالج
                st_frame.image(res_plotted, channels="BGR", use_container_width=True)
            else:
                vid_cap.release()
                break