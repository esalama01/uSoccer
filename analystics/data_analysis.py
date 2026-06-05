import pandas as pd
from matplotlib.colors import Normalize
import matplotlib.patches as patches
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import json

with open('/home/esalama/PycharmProjects/uSoccer/analystics/plot_config.json', 'r') as file:
    config = json.load(file)

height = float(config["height"])
width = float(config["width"])

class Plots:
    def __init__(self,read_path = "../data/spadl", columns = None, filters = None):
        self.data = pd.read_parquet(
            read_path,
            engine='pyarrow',
            filters=filters  # To filter out games by their ids.(ex: filters=[('game_id', '=', 1914251)])
        )
        cat_cols = self.data.select_dtypes(include=['category']).columns
        self.data[cat_cols] = self.data[cat_cols].astype('object')  # converting game_id to string.
        unique_teams = self.data['team_id'].unique()
        self.home_team_id = unique_teams[0]
        if self.data is not None:
            print(f"The data of {len(self.data)} games loaded.")
            

    def point_to_meters(self,p):
        '''
        Convert a point's coordinates from a 0-1 range to meters.
        '''
        return np.array([p[0] * width, p[1] * height])

    def draw_pitch(self, min_x=0, max_x=1):
        """
        Plot an empty horizontal football pitch, returning Matplotlib's ax object so we can keep adding elements to it.

        Parameters
        -----------
            min_x: float value from 0 to 'max_x' to choose a subsection of the pitch. Default value is 0.
            max_x: float value from 'min_x' to 1 to choose a subsection of the pitch. Default value is 1.

        Returns
        -----------
           ax : Matplotlib's axis object to keet adding elements on the pitch.
        """
        background_color = config["background_color"]
        lines_color = config["lines_color"]
        fig_size = config["fig_size"]

        # This allows to plot a subsection of the pitch
        ratio = height / float((width * max_x) - (width * min_x))
        f, ax = plt.subplots(1, 1, figsize=(fig_size, fig_size * ratio), dpi=100)

        ax.set_ylim([0, height])
        ax.set_xlim([width * min_x, width * max_x])
        ax.add_patch(patches.Rectangle((0, 0), width, height, color=background_color))

        # Plot outer lines
        line_pts = [
            [self.point_to_meters([0, 0]), self.point_to_meters([0, 1])],  # left line
            [self.point_to_meters([1, 0]), self.point_to_meters([1, 1])],  # right line
            [self.point_to_meters([0, 1]), self.point_to_meters([1, 1])],  # top line
            [self.point_to_meters([0, 0]), self.point_to_meters([1, 0])],  # bottom line
        ]

        for line_pt in line_pts:
            ax.plot([line_pt[0][0], line_pt[1][0]], [line_pt[0][1], line_pt[1][1]], '-',
                    alpha=0.8, lw=1.5, zorder=3, color=lines_color)

        # Plot boxes
        line_pts = [
            [self.point_to_meters([0.5, 0]), self.point_to_meters([0.5, 1])],  # center line

            # left box
            [[0, 24.85], [0, 2.85]],
            [[0, 13.85], [16.5, 13.85]],
            [[0, 54.15], [16.5, 54.15]],
            [[16.5, 13.85], [16.5, 54.15]],

            # left goal
            [[0, 24.85], [5.5, 24.85]],
            [[0, 43.15], [5.5, 43.15]],
            [[5.5, 24.85], [5.5, 43.15]],

            # right box
            [[105, 24.85], [105, 2.85]],
            [[105, 13.85], [88.5, 13.85]],
            [[105, 54.15], [88.5, 54.15]],
            [[88.5, 13.85], [88.5, 54.15]],

            # right goal
            [[105, 24.85], [99.5, 24.85]],
            [[105, 43.15], [99.5, 43.15]],
            [[99.5, 24.85], [99.5, 43.14]]
        ]

        for line_pt in line_pts:
            ax.plot([line_pt[0][0], line_pt[1][0]], [line_pt[0][1], line_pt[1][1]], '-',
                    alpha=0.8, lw=1.5, zorder=3, color=lines_color)

        # Plot circles
        ax.add_patch(patches.Wedge((94.0, 34.0), 9, 130, 230, fill=True, edgecolor=lines_color,
                                   facecolor=lines_color, zorder=4, width=0.02, alpha=0.8))

        ax.add_patch(patches.Wedge((11.0, 34.0), 9, 310, 50, fill=True, edgecolor=lines_color,
                                   facecolor=lines_color, zorder=4, width=0.02, alpha=0.8))

        ax.add_patch(patches.Wedge((52.5, 34), 9.5, 0, 360, fill=True, edgecolor=lines_color,
                                   facecolor=lines_color, zorder=4, width=0.02, alpha=0.8))

        plt.axis('off')
        return ax

    def draw_pass_map(ax, player_position,
                      player_pass_count, player_pass_value, pair_pass_count, pair_pass_value, title="", legend="",
                      max_player_count=None, max_player_value=None, max_pair_count=None, max_pair_value=None):
        """
        Plot a passing network.

        Parameters
        -----------
            ax: Matplotlib's axis object, it expects to have the pitch already plotted.
            player_position: pandas DataFrame with player names as index and columns 'origin_pos_x' and 'origin_pos_y' in 105-68 meters range.
            player_pass_count: pandas DataFrame with player names as index and a column 'num_passes'.
            player_pass_value: pandas DataFrame with player names as index and a column 'pass_value'.
            pair_pass_count: pandas DataFrame with 'player1_player2' as index and a column 'num_passes'.
            pair_pass_value: pandas DataFrame with 'player1_player2' as index and a column 'pass_value'.
            title: text that will be shown above the pitch.
            legend: text that will be shown in the bottom-left corner of the pitch.
            max_player_count: max number of passes per player. If not specified, it uses the player_pass_count.num_passes.max()
            max_player_value: max pass value per player. If not specified, it uses the player_pass_value.pass_value.max()
            max_pair_count: max number of passes per player pair. If not specified, it uses the pair_pass_count.num_passes.max()
            max_pair_value: max pass value per player pair. If not specified, it uses the pair_pass_value.pass_value.max()

        Returns
        -----------
           ax : Matplotlib's axis object to keep adding elements on the pitch.
        """
        background_color = config["background_color"]


        # This allows to fix the range of sizes and color scales so that two plots from different teams are comparable.
        max_player_count = player_pass_count.num_passes.max() if max_player_count is None else max_player_count
        max_player_value = player_pass_value.pass_value.max() if max_player_value is None else max_player_value
        max_pair_count = pair_pass_count.num_passes.max() if max_pair_count is None else max_pair_count
        max_pair_value = pair_pass_value.pass_value.max() if max_pair_value is None else max_pair_value

        # Step 1: plot edges
        if config["plot_edges"]:
            # Combine num_passes and pass_value columns into one DataFrame
            pair_stats = pd.merge(pair_pass_count, pair_pass_value, left_index=True, right_index=True)
            for pair_key, row in pair_stats.iterrows():
                player1, player2 = pair_key.split("_")

                player1_x = player_position.loc[player1]["origin_pos_x"]
                player1_y = player_position.loc[player1]["origin_pos_y"]

                player2_x = player_position.loc[player2]["origin_pos_x"]
                player2_y = player_position.loc[player2]["origin_pos_y"]

                num_passes = row["num_passes"]
                pass_value = row["pass_value"]

                line_width = _change_range(num_passes, (0, max_pair_count),
                                           (config["min_edge_width"], config["max_edge_width"]))
                norm = Normalize(vmin=0, vmax=max_pair_value)
                edge_cmap = cm.get_cmap(config["nodes_cmap"])
                edge_color = edge_cmap(norm(pass_value))

                ax.plot([player1_x, player2_x], [player1_y, player2_y],
                        'w-', linestyle='-', alpha=1, lw=line_width, zorder=3, color=edge_color)

        # Step 2: plot nodes
        # Combine num_passes and pass_value columns into one DataFrame
        player_stats = pd.merge(player_pass_count, player_pass_value, left_index=True, right_index=True)
        for player_name, row in player_stats.iterrows():
            player_x = player_position.loc[player_name]["origin_pos_x"]
            player_y = player_position.loc[player_name]["origin_pos_y"]

            num_passes = row["num_passes"]
            pass_value = row["pass_value"]

            marker_size = _change_range(num_passes, (0, max_player_count),
                                        (config["min_node_size"], config["max_node_size"]))
            norm = Normalize(vmin=0, vmax=max_player_value)
            node_cmap = cm.get_cmap(config["nodes_cmap"])
            node_color = node_cmap(norm(pass_value))

            ax.plot(player_x, player_y, '.', color=node_color, markersize=marker_size, zorder=5)
            ax.plot(player_x, player_y, '.', color=background_color, markersize=marker_size - 20, zorder=6)
            ax.annotate(player_name, xy=(player_x, player_y), ha="center", va="center", zorder=7,
                        fontsize=config["font_size"], color=config["font_color"], weight='bold',
                        path_effects=[pe.withStroke(linewidth=2, foreground=background_color)])

        # Step 3: Extra information shown on the plot
        ax.annotate("@SergioMinuto90", xy=(0.99 * width, 0.02 * height),
                    ha="right", va="bottom", zorder=7, fontsize=10, color=config["lines_color"])

        if legend:
            ax.annotate(legend, xy=(0.01 * width, 0.02 * height),
                        ha="left", va="bottom", zorder=7, fontsize=10, color=config["lines_color"])

        if title:
            ax.set_title(title, loc="left")

        return ax

    def prepare_data(self):


def main():
    ax = Plots()
    ax.draw_pitch()
    plt.savefig("first.png".format(ax.draw_pitch()))

if __name__ == "__main__":
    main()