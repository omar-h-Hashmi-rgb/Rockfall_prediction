import streamlit as st
import os
from pathlib import Path
from PIL import Image
import numpy as np
import pandas as pd
import plotly.express as px

st.set_page_config(page_title='Imagery Analysis', page_icon='🛰️', layout='wide')

# CSS for text visibility
st.markdown("""
<style>
    /* Ensure all text is visible on dark theme */
    .stMarkdown, .stMarkdown p, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {
        color: #ecf0f1 !important;
    }
    
    /* Input labels */
    .stTextInput label, .stSelectbox label, .stNumberInput label, .stCheckbox label, .stSlider label {
        color: #ecf0f1 !important;
        font-weight: bold !important;
    }
    
    /* Tab labels */
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        color: #ecf0f1 !important;
    }
</style>
""", unsafe_allow_html=True)

# Check authentication
if not st.session_state.get('auth', False):
    st.error("🔒 Please log in to access imagery analysis")
    st.stop()

st.title('🛰️ Drone Imagery & Analysis')

# Data paths
DATA_ROOT = Path(__file__).resolve().parents[2] / 'data' / 'DroneImages' / 'FilteredData'
IMAGES_DIR = DATA_ROOT / 'Images'
MASKS_DIR = DATA_ROOT / 'Masks'
BINARY_DIR = DATA_ROOT / 'BinaryMasks'

def load_sample_images(directory: Path, limit: int = 20):
    """Load sample images from directory."""
    if not directory.exists():
        return []
    
    supported_formats = ['.png', '.jpg', '.jpeg', '.tif', '.tiff']
    image_files = []
    
    for ext in supported_formats:
        image_files.extend(list(directory.glob(f'*{ext}')))
        image_files.extend(list(directory.glob(f'*{ext.upper()}')))
    
    return sorted(image_files)[:limit]

def analyze_image_stats(image_path: Path):
    """Analyze image statistics."""
    try:
        with Image.open(image_path) as img:
            img_array = np.array(img.convert('L'))  # Convert to grayscale
            
            return {
                'size': img.size,
                'mode': img.mode,
                'brightness': np.mean(img_array),
                'contrast': np.std(img_array),
                'min_intensity': np.min(img_array),
                'max_intensity': np.max(img_array)
            }
    except Exception as e:
        return {'error': str(e)}

# Sidebar controls
with st.sidebar:
    st.markdown("### 🎛️ Analysis Controls")
    
    sample_size = st.slider(
        "📊 Sample Size", 
        min_value=5, 
        max_value=50, 
        value=12,
        help="Number of images to display"
    )
    
    show_stats = st.checkbox("📈 Show Image Statistics", value=True)
    show_masks = st.checkbox("🎭 Show Masks", value=True)
    show_binary = st.checkbox("⚫ Show Binary Masks", value=True)
    
    analysis_mode = st.selectbox(
        "🔍 Analysis Mode",
        ["Gallery View", "Comparison View", "Statistical Analysis"],
        help="Choose how to display the imagery data"
    )

# Main content area
if analysis_mode == "Gallery View":
    st.markdown("### 📸 Image Gallery")
    
    # Create tabs for different image types
    tabs = ["🖼️ Original Images"]
    if show_masks:
        tabs.append("🎭 Segmentation Masks")
    if show_binary:
        tabs.append("⚫ Binary Masks")
    
    tab_objects = st.tabs(tabs)
    
    # Original Images Tab
    with tab_objects[0]:
        st.markdown("#### 📷 Drone Images")
        
        image_files = load_sample_images(IMAGES_DIR, sample_size)
        
        if image_files:
            cols = st.columns(4)
            
            for idx, img_path in enumerate(image_files):
                col_idx = idx % 4
                
                with cols[col_idx]:
                    try:
                        img = Image.open(img_path)
                        st.image(img, caption=img_path.name, use_column_width=True)
                        
                        if show_stats:
                            stats = analyze_image_stats(img_path)
                            if 'error' not in stats:
                                with st.expander("📊 Stats"):
                                    st.write(f"Size: {stats['size'][0]}×{stats['size'][1]}")
                                    st.write(f"Brightness: {stats['brightness']:.1f}")
                                    st.write(f"Contrast: {stats['contrast']:.1f}")
                    except Exception as e:
                        st.error(f"Error loading {img_path.name}: {str(e)}")
        else:
            st.warning("📂 No images found in the Images directory")
            st.info(f"**Expected path:** `data/DroneImages/FilteredData/Images/`")
            st.info(f"**Data location:** `{DATA_ROOT}`")
            
            # Production-friendly message
            st.markdown("""
            ---
            ℹ️ **Note for Production Deployment:**
            
            Drone imagery files are not included in the Git repository due to their large size. 
            
            **To enable imagery analysis:**
            1. Upload sample images to a cloud storage service (AWS S3, Google Cloud Storage, etc.)
            2. Update the data path in the configuration
            3. Or run this application locally where the image files are available
            
            **Current Status:**
            - ✅ API and Database: Connected
            - ✅ Sensors & Predictions: Working
            - ⏸️ Imagery: Awaiting image data upload
            """)
    
    # Masks Tab
    if show_masks and len(tab_objects) > 1:
        with tab_objects[1]:
            st.markdown("#### 🎭 Segmentation Masks")
            
            mask_files = load_sample_images(MASKS_DIR, sample_size)
            
            if mask_files:
                cols = st.columns(4)
                
                for idx, mask_path in enumerate(mask_files):
                    col_idx = idx % 4
                    
                    with cols[col_idx]:
                        try:
                            mask = Image.open(mask_path)
                            st.image(mask, caption=mask_path.name, use_column_width=True)
                        except Exception as e:
                            st.error(f"Error loading {mask_path.name}: {str(e)}")
            else:
                st.warning("📂 No mask files found in the Masks directory")
    
    # Binary Masks Tab
    if show_binary and len(tab_objects) > (2 if show_masks else 1):
        tab_idx = 2 if show_masks else 1
        with tab_objects[tab_idx]:
            st.markdown("#### ⚫ Binary Masks")
            
            binary_files = load_sample_images(BINARY_DIR, sample_size)
            
            if binary_files:
                cols = st.columns(4)
                
                for idx, binary_path in enumerate(binary_files):
                    col_idx = idx % 4
                    
                    with cols[col_idx]:
                        try:
                            binary = Image.open(binary_path)
                            st.image(binary, caption=binary_path.name, use_column_width=True)
                        except Exception as e:
                            st.error(f"Error loading {binary_path.name}: {str(e)}")
            else:
                st.warning("📂 No binary mask files found in the BinaryMasks directory")

elif analysis_mode == "Comparison View":
    st.markdown("### 🔍 Side-by-Side Comparison")
    
    # Get file lists
    image_files = load_sample_images(IMAGES_DIR, sample_size)
    mask_files = load_sample_images(MASKS_DIR, sample_size)
    binary_files = load_sample_images(BINARY_DIR, sample_size)
    
    if image_files:
        # Image selector
        selected_idx = st.selectbox(
            "📋 Select Image", 
            range(len(image_files)),
            format_func=lambda x: image_files[x].name
        )
        
        selected_image = image_files[selected_idx]
        
        # Display comparison
        cols = st.columns(3)
        
        with cols[0]:
            st.markdown("#### 📷 Original Image")
            try:
                img = Image.open(selected_image)
                st.image(img, use_column_width=True)
                
                # Image info
                stats = analyze_image_stats(selected_image)
                if 'error' not in stats:
                    st.info(f"""
                    **Image Properties:**
                    - Size: {stats['size'][0]} × {stats['size'][1]}
                    - Brightness: {stats['brightness']:.1f}
                    - Contrast: {stats['contrast']:.1f}
                    """)
            except Exception as e:
                st.error(f"Error loading image: {str(e)}")
        
        with cols[1]:
            st.markdown("#### 🎭 Segmentation Mask")
            
            # Try to find corresponding mask
            mask_name = selected_image.stem
            corresponding_mask = None
            
            for mask_file in mask_files:
                if mask_name in mask_file.stem or mask_file.stem in mask_name:
                    corresponding_mask = mask_file
                    break
            
            if corresponding_mask:
                try:
                    mask = Image.open(corresponding_mask)
                    st.image(mask, use_column_width=True)
                    st.success(f"✅ Found: {corresponding_mask.name}")
                except Exception as e:
                    st.error(f"Error loading mask: {str(e)}")
            else:
                if mask_files:
                    # Show first available mask
                    try:
                        mask = Image.open(mask_files[0])
                        st.image(mask, use_column_width=True)
                        st.warning(f"⚠️ Showing: {mask_files[0].name}")
                    except Exception as e:
                        st.error(f"Error loading mask: {str(e)}")
                else:
                    st.warning("No mask files available")
        
        with cols[2]:
            st.markdown("#### ⚫ Binary Mask")
            
            # Try to find corresponding binary mask
            corresponding_binary = None
            
            for binary_file in binary_files:
                if mask_name in binary_file.stem or binary_file.stem in mask_name:
                    corresponding_binary = binary_file
                    break
            
            if corresponding_binary:
                try:
                    binary = Image.open(corresponding_binary)
                    st.image(binary, use_column_width=True)
                    st.success(f"✅ Found: {corresponding_binary.name}")
                except Exception as e:
                    st.error(f"Error loading binary mask: {str(e)}")
            else:
                if binary_files:
                    # Show first available binary mask
                    try:
                        binary = Image.open(binary_files[0])
                        st.image(binary, use_column_width=True)
                        st.warning(f"⚠️ Showing: {binary_files[0].name}")
                    except Exception as e:
                        st.error(f"Error loading binary mask: {str(e)}")
                else:
                    st.warning("No binary mask files available")

elif analysis_mode == "Statistical Analysis":
    st.markdown("### 📊 Statistical Analysis")
    
    # Analyze multiple images for statistics
    image_files = load_sample_images(IMAGES_DIR, min(sample_size, 30))  # Limit for performance
    
    if image_files:
        with st.spinner("🔄 Analyzing images..."):
            stats_data = []
            
            for img_path in image_files:
                stats = analyze_image_stats(img_path)
                if 'error' not in stats:
                    stats['filename'] = img_path.name
                    stats_data.append(stats)
        
        if stats_data:
            df_stats = pd.DataFrame(stats_data)
            
            # Summary statistics
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📈 Brightness Distribution")
                fig_bright = px.histogram(
                    df_stats, 
                    x='brightness', 
                    nbins=20,
                    title="Image Brightness Distribution"
                )
                st.plotly_chart(fig_bright, use_container_width=True)
            
            with col2:
                st.markdown("#### 📊 Contrast Analysis")
                fig_contrast = px.histogram(
                    df_stats, 
                    x='contrast', 
                    nbins=20,
                    title="Image Contrast Distribution"
                )
                st.plotly_chart(fig_contrast, use_container_width=True)
            
            # Scatter plot
            st.markdown("#### 🔍 Brightness vs Contrast")
            fig_scatter = px.scatter(
                df_stats,
                x='brightness',
                y='contrast',
                hover_data=['filename'],
                title="Brightness vs Contrast Relationship"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            # Summary table
            st.markdown("#### 📋 Summary Statistics")
            summary_stats = df_stats[['brightness', 'contrast']].describe()
            st.dataframe(summary_stats, use_container_width=True)
            
            # Individual image stats
            with st.expander("🔍 Detailed Image Statistics"):
                st.dataframe(df_stats, use_container_width=True)
        else:
            st.error("❌ Could not analyze any images")
    else:
        st.warning("📂 No images found for analysis")

# Footer information
st.markdown("---")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📁 Images Found", len(load_sample_images(IMAGES_DIR, 1000)))

with col2:
    st.metric("🎭 Masks Found", len(load_sample_images(MASKS_DIR, 1000)))

with col3:
    st.metric("⚫ Binary Masks Found", len(load_sample_images(BINARY_DIR, 1000)))

st.caption(f"📂 Data location: {DATA_ROOT}")