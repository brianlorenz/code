from uncover_read_data import read_slit_loc_cat
from astropy import units as u
from astropy.coordinates import SkyCoord
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def plot_shutter_pos(ax, id_msa, wcs):
    slit_loc_df = read_slit_loc_cat()
    slit_loc_rows = slit_loc_df[slit_loc_df['id_msa']==id_msa]
    for i in range(len(slit_loc_rows)):
        row = slit_loc_rows.iloc[i]
        shutter_strs = [row['SRC_SHUT_S_REGION_1'], row['SHUT_S_REGION_0'], row['SHUT_S_REGION_2']]
        for shutter_str in shutter_strs:
            box_coords = split_shutter_to_radec(shutter_str)
            pixel_locations = [wcs.world_to_pixel(coord) for coord in box_coords]

            # Define the corners of the rectangle
            x1, y1 = pixel_locations[0][0], pixel_locations[0][1]  # Bottom left corner
            x2, y2 = pixel_locations[1][0], pixel_locations[1][1]  # Bottom right corner
            x3, y3 = pixel_locations[2][0], pixel_locations[2][1]  # Top right corner
            x4, y4 = pixel_locations[3][0], pixel_locations[3][1]  # Top left corner

            # Create a Polygon patch
            rect = patches.Polygon([(x1, y1), (x2, y2), (x3, y3), (x4, y4)], closed=True, fill=False, color='cyan')

            # Add the patch to the axes
            ax.add_patch(rect)

    return


def split_shutter_to_radec(shutter_str):
    split_str = shutter_str.split()
    box_coords = []
    for i in range(4):
        coord = SkyCoord(ra=float(split_str[2*i+2])*u.degree, dec=float(split_str[2*i+3])*u.degree)
        box_coords.append(coord)  
    return box_coords

if __name__ == "__main__":
    # plot_shutter_pos(1, 47875)
    pass