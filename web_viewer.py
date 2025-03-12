import streamlit as st
import tempfile
from streamlit_stl import stl_from_file

def main():
    st.set_page_config(layout="wide")
    st.title("STL File Viewer")
    
    # File input
    st.subheader("Upload an STL file")
    file_input = st.file_uploader("Choose an STL file", type=["stl"])
    
    if file_input:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".stl") as temp_file:
            temp_file.write(file_input.getvalue())
            temp_path = temp_file.name
        
        st.subheader("Customize View")
        
        # UI controls for customization
        cols = st.columns(5)
        with cols[0]:
            color = st.color_picker("Pick a color", "#FF9900", key='color')
        with cols[1]:
            material = st.selectbox("Select a material", ["material", "flat", "wireframe"], key='material')
        with cols[2]:
            auto_rotate = st.toggle("Auto rotate", key='auto_rotate')
        with cols[3]:
            opacity = st.slider("Opacity", min_value=0.0, max_value=1.0, value=1.0, key='opacity')
        with cols[4]:
            height = st.slider("Height", min_value=50, max_value=1000, value=500, key='height')

        cols = st.columns(4)
        with cols[0]:
            cam_v_angle = st.number_input("Camera Vertical Angle", value=60, key='cam_v_angle')
        with cols[1]:
            cam_h_angle = st.number_input("Camera Horizontal Angle", value=-90, key='cam_h_angle')
        with cols[2]:
            cam_distance = st.number_input("Camera Distance", value=0, key='cam_distance')
        with cols[3]:
            max_view_distance = st.number_input("Max view distance", min_value=1, value=1000, key='max_view_distance')

        # Render STL file
        stl_from_file(
            file_path=temp_path,
            color=color,
            material=material,
            auto_rotate=auto_rotate,
            opacity=opacity,
            height=height,
            shininess=100,
            cam_v_angle=cam_v_angle,
            cam_h_angle=cam_h_angle,
            cam_distance=cam_distance,
            max_view_distance=max_view_distance,
            key='stl_viewer'
        )

if __name__ == "__main__":
    main()