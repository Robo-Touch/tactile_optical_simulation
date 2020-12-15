Tactile optical simulation
============================
# Setup
The project uses a [modified fork](https://github.com/arpit15/mitsuba/tree/lights) of [Mitsuba renderer](https://github.com/mitsuba-renderer/mitsuba)(v0.6.0) for generating all the images. Please download the renderer from [here](https://www.mitsuba-renderer.org/download.html) or build from source according to [official documentation](http://mitsuba-renderer.org/docs.html) 

# Usage
- `python generate_image.py`
- To choose the configuration file see files inside `file_list_cfgs`
- To choose the render configurations see files inside `render_cfgs`

# Visualization
[qt4Image](https://github.com/edgarv/hdritools) gives consistent visualization for exr images across different platform. It can also generate low-dynamic range images with gamma encoding. You can download the utility for linux from [this](https://github.com/edgarv/hdritools/releases/download/0.5.0/qt4Image-Qt5_0.5.0-20170712-win64-amd64-vc141.zip) link.

# Advanced
- The model files for GelSight are in Mitsuba xml format. The [Mitsuba documentation](http://mitsuba-renderer.org/docs.html) has details on the parameters and how to set them. 
- The important files which are used in rendering for flatgel is `models/flatgel_with_mesh.xml` or `models/flatgel_with_hf.xml` 