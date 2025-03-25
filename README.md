### Introduction

A tool to convert depth map (.mp4) files into point cloud (.ply) files. Each video frame is converted individually and sequentially resulting in n output files where n is the length of the input .mp4 file in frames. Additionally, this tool leverages Open 3Ds point cloud visualisation and update methods to simulate video playback for sequential point cloud files.

This tool was designed and tested to work on Windows 11, other operating systems may require a multitude of method adjustments for it to function as intended. Furthermore, the "requirements-dc.txt" requirements file for this project reflects dependencies required for the DepthCrafter (RGB to generated Depth Video) project created by Tencent. These were included as the current project does not reflect an appropriate installation method for certain dependencies when setting things up from a base/new environment. If not utilising the application to generate depth videos prior to point cloud generation it can be ignored.

### Installation

1. Clone this repo:
```bash
git clone https://github.com/x-ix/DepthToPoint.git
```
2. Install dependencies (please refer to [requirements.txt](requirements.txt)):
```bash
pip install -r requirements.txt
```
3. (Optional) Install DepthCrafter dependencies (please refer to [requirements-dc.txt](requirements-dc.txt)):
```bash
pip install -r requirements-dc.txt
```
Please take care to not overwrite the dc dependencies with those included in the original DepthCrafter project.

### Usage
```
Usage:
    python DepthToPoint.py [options]

Options:
    test [<depth_video_path>] [options]
    test is used to experiment with and visualise outputs prior to saving

    save [<depth_video_path>] [<output_name>] [options]
    save generates and saves point cloud files without visualisation

    view [<folder_path>] [options]
    view allows for playback of existing .ply files that are direct children of a specified directory

test Options:
    --truncation_threshold [<float>], -t [<float>] : Removes points in the background on the cloud based on the specified value/distance
    --distance_offset [<float>], -d [float] : Pushes the cloud further from the point of origin if the front is too bunched up
    --loop, -l : Loops playback

save Options:
    --truncation_threshold [<float>], -t [<float>] : Removes points in the background on the cloud based on the specified value/distance
    --distance_offset [<float>], -d [float] : Pushes the cloud further from the point of origin if the front is too bunched up

view Options:
    --loop, -l : Loops playback
```

### Examples:
Testing the output of depth_video.mp4 with a truncation threshold of 77 and distance offset of 7 with looping playback:
```bash
    python DepthToPoint.py test folder/depth_video.mp4 -t 77 -d 7 -l
```

Saving the output of depth_video.mp4 with no modifiers under the name clouds:
```bash
    python DepthToPoint.py save folder/depth_video.mp4 clouds
```

Viewing a looped playback of the point cloud files located in a folder:
```bash
    python DepthToPoint.py view point/cloud/folder -l
```

### Miscellanious
Contents of [requirements.txt](requirements.txt):
```
tqdm==4.67.1
numpy==1.26.4
open3d==0.19.0
av==14.2.0
```

Contents of [requirements-dc.txt](requirements-dc.txt):
```
--index-url https://download.pytorch.org/whl/cu118
torch==2.0.1 
torchvision==0.15.2
torchaudio==2.0.2

--extra-index-url https://pypi.org/simple
diffusers==0.29.1
matplotlib==3.8.4
transformers==4.41.2
accelerate==0.30.1
xformers==0.0.20
mediapy==1.2.0
fire==0.6.0
decord==0.6.0
OpenEXR==3.2.4
```

### Closing Notes
I don't think anyone else will ever need to use this but if you do, it took me a little while to put together so thank you :)
