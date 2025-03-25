from tqdm import tqdm
import numpy as np
import open3d as o3d
from time import sleep
from pathlib import Path
import os
import sys
import glob
import argparse
import av

#---------------------
VIEW_SLEEP_DURATION = 0.0318 #time each frame of a point cloud is displayed in the viewer when reading existing files
TEST_SLEEP_DURATION = 0.0416666667 #when generating new point clouds
ROOT_FOLDER = "saved_pointclouds" #static folder to save point clouds in
X_AXIS_FOCAL_LENGTH = 500 #theoretical camera focal length parameters when setting open3d camera intrinsics
Y_AXIS_FOCAL_LENGTH = 500
ARTIFICIALLY_ADDED_DISTANCE = 50

#---------------------
def initialise_progress_bar(total):
    return tqdm(total=total, desc="Processing", unit="step")

def truncate(frame_data, threshold):

    #removes data points past a certain distance from the background
    frame_data[frame_data <= threshold] = 0 
    return frame_data



def pcd_flip(pcd):

    #180 degree flip of pcd so it doesn't render upsidedown
    pcd.transform([[1,  0,  0,  0], #180 degree flip as the point cloud starts off backwards
               [0, -1,  0,  0],
               [0,  0, -1,  0],
               [0,  0,  0,  1]])
    return pcd



def create_visualiser(pcd):

    #Create a visualiser and display the first generated/read point cloud.
    #This gives scope to update the visualisers renderer when new point clouds are generated to create a pseudo video playback experience.
    vis = o3d.visualization.Visualizer()
    vis.create_window()
    pcd = pcd_flip(pcd)
    vis.add_geometry(pcd)
    vis.poll_events()
    vis.update_renderer()
    return vis



def update_visualiser(vis, pcd, sleep_duration):

    #makes visualiser window display the latest rendition of pcd
    pcd = pcd_flip(pcd)
    vis.update_geometry(pcd)
    vis.poll_events()
    vis.update_renderer()
    sleep(sleep_duration)



def retrieve_point_cloud_path_list(path):

    #catch errors involving incorrect and incompatible paths
    if not os.path.isdir(path):
        print("Invalid path")
        sys.exit()
    ply_paths = sorted(glob.glob(f"{path}/*.ply"))
    if not ply_paths:
        print("No point cloud files found")
        sys.exit()
    return ply_paths


    
def initial_existing_file_visualisation(ply_paths, pbar):

    #create visualiser and display first frame
    pcd = o3d.io.read_point_cloud(f"{ply_paths[0]}")
    vis = create_visualiser(pcd)
    pbar.update(1)    
    return pcd, vis



def visualise_existing_files(ply_paths, pcd, vis, pbar, array_index):

    #refresh visualiser for all subsequent ply files/frames
    for ply in ply_paths[array_index:]:
        pcd.points = o3d.io.read_point_cloud(f"{ply}").points
        update_visualiser(vis, pcd, VIEW_SLEEP_DURATION)
        pbar.update(1)



def generate_pcd(frame, truncation_threshold, distance_offset, intrinsic, initial_pcd=False):

    #pre-processing
    frame_data = (frame.to_ndarray(format="gray")).astype(np.float32) #greyscale image, working with float32 so normalisation is possible
    if truncation_threshold:
        frame_data = truncate(frame_data, truncation_threshold)

    #turn into point cloud
    frame_data = frame_data.max() - frame_data #Depth Crafter outputs large values for close objects and near-zero for far ones
                                                    #o3d expects the opposite in scale so the frame data needs to be inverted
    frame_data = frame_data + frame_data.min() + distance_offset #pulling values to be positive

    depth_image = o3d.geometry.Image(frame_data)
    pcd = o3d.geometry.PointCloud.create_from_depth_image(depth_image, intrinsic)
    #np.savetxt("pointcloud.txt", np.asarray(pcd.points))
    #sys.exit()
    if initial_pcd == True:
        return pcd
    else:
        return pcd.points



def create_save_folders(name):

    #root and sub folder checks/creation for saving point clouds
    os.makedirs(ROOT_FOLDER, exist_ok=True)
    folder_path = os.path.join(ROOT_FOLDER, name)
    if os.path.isdir(folder_path) and os.listdir(folder_path):
         print("ERROR: Folder already exists and is not empty. Please empty existing folder or try again with a new, distinct name.")
         sys.exit()
    os.makedirs(folder_path, exist_ok=True)



def save(pcd, name, frame_count):

    #saving point clouds with numbered suffix so the frames can be in order (alphabetically)
    frame_count += 1
    o3d.io.write_point_cloud(os.path.join(ROOT_FOLDER, name) + "/" + name + "_" + f"{frame_count:05d}" + ".ply" , pcd)
    return frame_count



def set_parser():
    parser = argparse.ArgumentParser(description="determine required functions")
    subparsers = parser.add_subparsers(dest="command", required=True)

    #arguments for saving a generated point cloud
    save = subparsers.add_parser("save", help="create and save point clouds")
    save.add_argument("video_path", type=str, help="Path to Original Video")
    save.add_argument("output_name", type=str, help="Name Point Clouds will be saved under")
    save.add_argument("--truncation_threshold", "-t", type=float, help="Removes points from the background forward below the specifed value")
    save.add_argument("--distance_offset", "-d", type=float, help="Moves the point cloud further from the point of origin by the input distance")

    #arguments when viewing a point cloud that is currently being generated to visualise output, tune values etc.
    test = subparsers.add_parser("test", help="create and visualise point clouds in real time")
    test.add_argument("video_path", type=str, help="Path to Original Video")
    test.add_argument("--truncation_threshold", "-t", type=float, help="Removes points from the background forward below the specifed value")
    test.add_argument("--loop", "-l", action="store_true", help="causes playback to loop if desired")
    test.add_argument("--distance_offset", "-d", type=float, help="Moves the point cloud further from the point of origin by the input distance")

    #arguments to view existing point clouds in their folders
    view = subparsers.add_parser("view", help="view existing point cloud files")
    view.add_argument("point_cloud_folder_path", type=str, help="Folder containing point clouds intended for display")
    view.add_argument("--loop", "-l", action="store_true", help="causes playback to loop if desired")

    return parser



def main():
    parser = set_parser()
    args = parser.parse_args()


    #runs function to view existing point cloud files, looping if requested
    if args.command == "view":
        if args.loop == True:
            print("Press Ctrl+C to end playback")
        ply_paths = retrieve_point_cloud_path_list(args.point_cloud_folder_path)
        pbar = initialise_progress_bar(len(ply_paths))
        pcd, vis = initial_existing_file_visualisation(ply_paths, pbar)
        array_index = 1
        while True:
            visualise_existing_files(ply_paths, pcd, vis, pbar, array_index)
            if args.loop == False:
                break
            array_index = 0
    else:
        container = av.open(args.video_path) #open video file
        stream = container.streams.video[0]  # Select our video from container

        #Setting our theoretical camera's settings/parameters
        width, height = stream.width, stream.height
        intrinsic = o3d.camera.PinholeCameraIntrinsic(width, height, X_AXIS_FOCAL_LENGTH, Y_AXIS_FOCAL_LENGTH, width / 2, height / 2)


        for frame in container.decode(stream):
            pcd = generate_pcd(frame, args.truncation_threshold, args.distance_offset, intrinsic, True)
            break
        if args.command == "save":
            frame_count = 0 #allows for iteration of saved point cloud's names
            create_save_folders(args.output_name)
            frame_count = save(pcd, args.output_name, frame_count) #save as .ply
        else:
            vis = create_visualiser(pcd)
        if not args.command == "save" and args.loop == True:
            print("Press Ctrl+C to end playback")
        pbar = initialise_progress_bar(stream.frames)
        pbar.update(1)

        #Either saves frames as point cloud files over one pass or renders point clouds on a loop if requested
        while True:
            #loop for creating point clouds for each frame of the input video
            for frame in container.decode(video=0):
                pcd.points = generate_pcd(frame, args.truncation_threshold, args.distance_offset, intrinsic)
                if args.command == "save":
                    frame_count = save(pcd, args.output_name, frame_count) #save as .ply
                else:
                    update_visualiser(vis, pcd, TEST_SLEEP_DURATION)
                pbar.update(1)
            if args.command == "save" or args.loop == False:
                break
            container = av.open(args.video_path) #open video file
            stream = container.streams.video[0]



if __name__ == "__main__": #to run itself
    try:
        main()
    except KeyboardInterrupt:
        pass  # Ignore the KeyboardInterrupt and exit silently