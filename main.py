import os
import re
from collections import defaultdict

BASE_DIR = "Z:/Movies/YTS/English"  # <-- Update this path

# Paths to resolution folders relative to BASE_DIR
RESOLUTION_FOLDERS = [
    os.path.join(BASE_DIR, folder)
    for folder in ["720p", "1080p", "1080p.x265", "2160p"]
]

# Dictionary to map resolution to a comparable integer value
RESOLUTION_PRIORITY = {"2160p": 4, "1080p.x265": 3, "1080p": 2, "720p": 1}

# Regular expression patterns for recognized resolution and quality tags
RESOLUTION_TAGS = r"\b(2160p|1080p\.x265|1080p|720p)\b"
QUALITY_TAGS = r"\b(BluRay|WEBRip)\b"

# Collect folders by title and year
folders_by_title = defaultdict(list)

# Step 1: Identify duplicates (only consider the immediate folders, no subdirectories)
for folder in RESOLUTION_FOLDERS:
    for dir_name in os.listdir(folder):  # List directories at the top level
        dir_path = os.path.join(folder, dir_name)
        if os.path.isdir(dir_path):
            # Use regex to extract title and year from folder name
            match = re.match(r"^(.*?) \((\d{4})\)", dir_name)
            if not match:
                print(f"Skipping unrecognized format: {dir_name}")
                continue

            title, year = match.groups()

            # Look for resolution and quality tags anywhere in the folder name
            resolution_match = re.search(RESOLUTION_TAGS, dir_name)
            quality_match = re.search(QUALITY_TAGS, dir_name)

            # If no resolution tag found, assume it based on the parent folder
            if resolution_match:
                resolution = resolution_match.group(1)
            else:
                # Extract resolution from the parent folder (e.g., '720p', '1080p', '1080p.x265', '2160p')
                resolution = os.path.basename(folder)
                if resolution not in RESOLUTION_PRIORITY:
                    print(
                        f"Skipping folder '{dir_name}' as no valid resolution tag or parent folder resolution found."
                    )
                    continue

            # Set quality if found; default to "Unknown" if not found
            quality = quality_match.group(1) if quality_match else "Unknown"

            # Record folder data
            folder_path = dir_path
            folders_by_title[(title, year)].append((folder_path, resolution, quality))

# Step 2: Identify the folders to keep and mark others for deletion
folders_to_delete = []

# Process each title-year pair
for (title, year), versions in folders_by_title.items():
    # Sort by resolution priority and quality preference
    sorted_versions = sorted(
        versions,
        key=lambda x: (RESOLUTION_PRIORITY.get(x[1], 0), x[2] == "BluRay"),
        reverse=True,
    )

    # Identify the highest resolution version
    highest_resolution = sorted_versions[0][1]
    keep = sorted_versions[
        0
    ]  # Keep the first (highest-resolution, BluRay-preferred) version

    # Mark all other versions for deletion if they have lower resolution or are WEBRip of the same resolution
    for version in sorted_versions[1:]:
        if RESOLUTION_PRIORITY[version[1]] < RESOLUTION_PRIORITY[
            highest_resolution
        ] or (version[1] == highest_resolution and version[2] != "BluRay"):
            folders_to_delete.append(version[0])

# Step 3: List folders to delete (optional print before deletion)
print("Folders to delete:")
for folder in folders_to_delete:
    print(folder)
