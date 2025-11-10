import uproot
import awkward as ak
import argparse
import logging
from tqdm import tqdm
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor

from processing import (
    get_event_data,
    gen_to_features,
    track_to_features,
    cluster_to_features,
    process_calo_hit_data,
    process_tracker_hit_data,
    create_track_to_hit_coo_matrix,
    create_cluster_to_hit_coo_matrix,
    genparticle_track_adj,
    create_genparticle_to_genparticle_coo_matrix,
)

### set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def process_single_root_file(root_file, output_dir, show_event_progress=False):
    """
    Process a single ROOT file and save to parquet format.
    
    Args:
        root_file (Path): Path to the ROOT file.
        output_dir (Path): Directory to save the parquet file.
        show_event_progress (bool): Whether to show progress bar for events.
    
    Returns:
        bool: True if processing was successful, False if skipped or failed.
    """
    try:
        output_file = output_dir / f"{root_file.stem}.parquet"
        if output_file.exists():
            logging.info(f"Output file {output_file} already exists. Skipping processing.")
            return False

        fi = uproot.open(root_file)
        collectionIDs = {
            k: v
            for k, v in zip(
                fi.get("podio_metadata").arrays("events___idTable/m_names")["events___idTable/m_names"][0],
                fi.get("podio_metadata").arrays("events___idTable/m_collectionIDs")["events___idTable/m_collectionIDs"][
                    0
                ],
            )
        }
        ev = fi["events"]
        event_data = get_event_data(ev)

        combined_data_dict = {
            "gen_features": [],
            "track_features": [],
            "cluster_features": [],
            "calo_hit_features": [],
            "tracker_hit_features": [],
            "genparticle_to_calo_hit_matrix": [],
            "genparticle_to_tracker_hit_matrix": [],
            "track_to_tracker_hit_matrix": [],
            "cluster_to_cluster_hit_matrix": [],
            "gp_to_track_matrix": [],
            "gp_to_gp": [],
        }

        ### set up event loop w/ a progress bar
        event_range = range(len(ev["MCParticles.momentum.x"].array()))
        if show_event_progress:
            event_range = tqdm(
                event_range,
                desc=f"Processing events in {root_file.name}",
                leave=False
            )

        for iev in event_range:
            gen_features = gen_to_features(event_data, iev)
            track_features = track_to_features(event_data, iev)
            cluster_features = cluster_to_features(
                event_data, iev, cluster_features=["position.x", "position.y", "position.z", "energy", "type"]
            )
            calo_hit_features, genparticle_to_calo_hit_matrix, _ = process_calo_hit_data(event_data, iev, collectionIDs)
            tracker_hit_features, genparticle_to_tracker_hit_matrix, _ = process_tracker_hit_data(
                event_data, iev, collectionIDs
            )
            track_to_tracker_hit_matrix, _ = create_track_to_hit_coo_matrix(event_data, iev, collectionIDs)
            cluster_to_cluster_hit_matrix, _ = create_cluster_to_hit_coo_matrix(event_data, iev, collectionIDs)
            gp_to_track_matrix = genparticle_track_adj(event_data, iev)
            gp_to_gp = create_genparticle_to_genparticle_coo_matrix(event_data, iev)

            combined_data_dict["gen_features"].append(gen_features)
            combined_data_dict["track_features"].append(track_features)
            combined_data_dict["cluster_features"].append(cluster_features)
            combined_data_dict["calo_hit_features"].append(calo_hit_features)
            combined_data_dict["tracker_hit_features"].append(tracker_hit_features)
            combined_data_dict["genparticle_to_calo_hit_matrix"].append(genparticle_to_calo_hit_matrix)
            combined_data_dict["genparticle_to_tracker_hit_matrix"].append(genparticle_to_tracker_hit_matrix)
            combined_data_dict["track_to_tracker_hit_matrix"].append(track_to_tracker_hit_matrix)
            combined_data_dict["cluster_to_cluster_hit_matrix"].append(cluster_to_cluster_hit_matrix)
            combined_data_dict["gp_to_track_matrix"].append(gp_to_track_matrix)
            combined_data_dict["gp_to_gp"].append(gp_to_gp)

        # Convert lists to ak arrays
        for key in combined_data_dict.keys():
            combined_data_dict[key] = ak.Array(combined_data_dict[key])

        ak.to_parquet(combined_data_dict, output_file)
        return True

    except Exception as e:
        logging.error(f"Error processing {root_file}: {e}")
        return False


def process_parallel(root_file_list, output_dir, max_workers=None):
    """
    Process ROOT files in parallel using ProcessPoolExecutor.
    
    Args:
        root_file_list (list): List of ROOT file paths.
        output_dir (Path): Directory to save parquet files.
        max_workers (int): Maximum number of parallel workers.
    """
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for root_file in root_file_list:
            futures.append(executor.submit(process_single_root_file, root_file, output_dir, False))

        processed_count = 0
        for future in tqdm(futures, desc="Processing ROOT files (parallel)"):
            if future.result():
                processed_count += 1

    logging.info(f"Finished processing {processed_count} ROOT files in parallel mode.")


def process_serial(root_file_list, output_dir):
    """
    Process ROOT files serially with detailed progress tracking.
    
    Args:
        root_file_list (list): List of ROOT file paths.
        output_dir (Path): Directory to save parquet files.
    """
    processed_count = 0
    for root_file in tqdm(root_file_list, desc="Processing ROOT files (serial)"):
        if process_single_root_file(root_file, output_dir, show_event_progress=True):
            processed_count += 1

    logging.info(f"Finished processing {processed_count} ROOT files in serial mode.")


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Process ROOT files and save features/matrices to parquet format."
    )
    parser.add_argument(
        "-i", "--input_dir",
        type=str,
        required=True,
        help="Directory containing ROOT files."
    )
    parser.add_argument(
        "-o", "--output_dir",
        type=str,
        default="./output",
        help="Directory to save parquet files."
    )
    parser.add_argument(
        "--max_root_files",
        type=int,
        default=None,
        help="Maximum number of ROOT files to process."
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Enable parallel processing using multiple CPU cores."
    )
    parser.add_argument(
        "--max_workers",
        type=int,
        default=None,
        help="Maximum number of parallel workers (only used with --parallel)."
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    ### make sure the output directory exists
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ### make sure the input directory exists
    input_dir = Path(args.input_dir)
    if not input_dir.is_dir():
        raise ValueError(f"Input directory {input_dir} does not exist or is not a directory.")

    ### get the full list of ROOT files
    root_file_list = sorted(list(input_dir.rglob("*.root")))
    if args.max_root_files:
        root_file_list = root_file_list[:args.max_root_files]

    logging.info(f"Found {len(root_file_list)} ROOT files to process.")
    logging.info(f"Processing mode: {'Parallel' if args.parallel else 'Serial'}")

    ### process files
    if args.parallel:
        process_parallel(root_file_list, output_dir, args.max_workers)
    else:
        process_serial(root_file_list, output_dir)

    ### load and display example file
    parquet_files = list(output_dir.glob("*.parquet"))
    if parquet_files:
        example_file = parquet_files[0]
        example_data = ak.from_parquet(example_file)

        logging.info(f"\nContents of example file {example_file}:")
        for key in example_data.fields:
            logging.info(f"  {key}: shape={len(example_data[key])}")
    else:
        logging.warning("No parquet files found in output directory.")
