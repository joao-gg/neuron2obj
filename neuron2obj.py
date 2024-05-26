import cloudvolume as cv
import argparse
import trimesh
import navis

import logging

logging.basicConfig(
    level  = logging.INFO, 
    format = "%(asctime)s - %(levelname)s - %(message)s"
)

def get_neuron_meshes(cloudpath, neuron_IDs, lod = 3):
    """
    Fetches neuron meshes from the given cloudpath.

    Args:
        cloudpath (str): The URL of the dataset.
        neuron_IDs (list[int]): List of neuron IDs to fetch.
        lod (int, optional): Level of detail for the mesh. Defaults to 3.

    Returns:
        navis.core.neuronlist.NeuronList: A list of neuron meshes.
    """
    try:
        cloud_vol = cv.CloudVolume(cloudpath=cloudpath, use_https=True, progress=False)
        mesh      = cloud_vol.mesh.get(neuron_IDs, as_navis=True, lod=lod)
        
        logging.info(f"Mesh successfully obtained from {cloudpath}")
        
        return mesh

    except Exception as e:
        logging.error(f"Error while fetching mesh from {cloudpath}: {e}")
        return None

def save_neuron_obj(neuron, filename):
    """
    Saves a neuron mesh as an OBJ file.

    Args:
        neuron (navis.MeshNeuron): The neuron mesh to save.
        filename (str): The filename to save the mesh as.
    """
    try:
        vertices = neuron.vertices
        faces    = neuron.faces
        mesh     = trimesh.Trimesh(vertices, faces)
        
        mesh.export(filename)

        logging.info(f"Exported mesh into: {filename}")

    except Exception as e:
        logging.error(f"Error while saving neuron mesh to {filename}: {e}")

def main(cloudpath, neuron_IDs, lod = 3):
    # patch cloud-volume with navis
    navis.patch_cloudvolume()

    meshes = get_neuron_meshes(cloudpath, neuron_IDs, lod)
    
    if meshes is None:
        logging.error("Error while fetching meshes from cloud-volume")
        return

    for neuron in meshes:
        filename = f"neuron_{neuron.id}.obj"
        save_neuron_obj(neuron, filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description = "Download neuron meshes and save as OBJ files."
    )
    
    parser.add_argument(
        "cloudpath", 
        type = str, 
        help = "URL of the dataset"
    )
    parser.add_argument(
        "neuron_IDs", 
        type = str, 
        help = "Comma-separated list of neuron IDs"
    )
    parser.add_argument(
        "--lod", 
        type    = int, 
        default = 3, 
        help    = "Level of detail for the mesh (default: 3)"
    )

    args = parser.parse_args()

    # convert neuron_IDs from comma-separated string to list[int]
    try:
        neuron_IDs = list(map(int, args.neuron_IDs.split(',')))

    except ValueError as e:
        logging.error(f"Invalid neuron ID(s): {e}")
        exit(1)

    main(args.cloudpath, neuron_IDs, args.lod)
