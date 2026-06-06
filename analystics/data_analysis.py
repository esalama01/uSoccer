import pandas as pd
from matplotlib.colors import Normalize
import matplotlib.patches as patches
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from matplotlib import cm
import numpy as np
import json
import xgboost
#from sklearn.model_selection import train_test_split
import os
from tqdm import tqdm

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
        self.data = self.data.sort_values('action_id')
        self.player_position = None
        self.pair_pass_value = None
        self.pair_pass_count = None
        self.player_pass_value = None
        self.player_pass_count = None
        self.data['pass_recipient_name'] = self.data['player_name'].shift(-1)
        self.data['next_team_name'] = self.data['team_name'].shift(-1)
        if self.data is not None:
            print(f"The data of {len(self.data)} games loaded.")

    def change_range(self,value, old_range, new_range):
        '''
        Convert a value from one range to another one, maintaining ratio.
        '''
        return ((value - old_range[0]) / (old_range[1] - old_range[0])) * (new_range[1] - new_range[0]) + new_range[0]

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

    def draw_pass_map(self,ax, player_position,
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

                line_width = self.change_range(num_passes, (0, max_pair_count),
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

            marker_size = self.change_range(num_passes, (0, max_player_count),
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
        ax.annotate("@esalama01", xy=(0.99 * width, 0.02 * height),
                    ha="right", va="bottom", zorder=7, fontsize=10, color=config["lines_color"])

        if legend:
            ax.annotate(legend, xy=(0.01 * width, 0.02 * height),
                        ha="left", va="bottom", zorder=7, fontsize=10, color=config["lines_color"])

        if title:
            ax.set_title(title, loc="left")

        return ax

    def prepare_data(self, period, num_minutes, team_name):
        """
                Prepares the five pandas DataFrames that 'draw_pass_map' needs.
                """
        # We select all successful passes done by the selected team before the minute

        df_passes = self.data[(self.data.type_name == "pass") &
                                   (self.data.result_name == 'success') &
                                   (self.data.team_name == team_name) &
                                   (self.data.period_id == period) &
                                   (self.data.time_seconds < num_minutes * 60)].copy()

        df_passes['pass_recipient_name'] = np.where(
            df_passes['team_name'] == df_passes['next_team_name'],
            df_passes['pass_recipient_name'],
            np.nan
        )
        df_passes = df_passes.dropna(subset=['pass_recipient_name']).copy()
        # In this type of plot, both the size and color (i.e. value) mean the same: number of passes
        self.player_pass_count = df_passes.groupby("player_name").size().to_frame("num_passes")
        self.player_pass_value = df_passes.groupby("player_name")['vaep_value'].sum().to_frame("pass_value")

        # 'pair_key' combines the names of the passer and receiver of each pass (sorted alphabetically)
        df_passes["pair_key"] = df_passes.apply(
            lambda x: "_".join(sorted([x["player_name"], x["pass_recipient_name"]])), axis=1)
        self.pair_pass_count = df_passes.groupby("pair_key").size().to_frame("num_passes")
        self.pair_pass_value = df_passes.groupby("pair_key")['vaep_value'].sum().to_frame("pass_value")
        # Average pass origin's coordinates for each player
        df_passes["origin_pos_x"] = df_passes['start_x']
        df_passes["origin_pos_y"] = df_passes['start_y']
        self.player_position = df_passes.groupby("player_name").agg({"origin_pos_x": "median", "origin_pos_y": "median"})


class Metrics:
    def __init__(self,read_path =  "../data/game_states", columns = None, filters = None):
        self.data = pd.read_parquet(
            read_path,
            engine='pyarrow',
            columns = columns,
            filters=filters  # To filter out games by their ids.(ex: filters=[('game_id', '=', 1914251)])
        )
    def select_features(self):
        X = self.data.drop(columns=['scores', 'concedes','goal_from_shot'])
        return X
    def select_labels(self):
        Y = self.data[['scores', 'concedes','goal_from_shot']]
        return Y

class VAEP(Metrics):
    def __init__(self,read_path =  "../data/game_states", columns = None, filters = None):
        super().__init__(read_path, columns, filters)
        self.target_cols = ['scores', 'concedes']
        self.model_scoring = None
        self.model_conceding = None
    def train(self):
        X = self.select_features(target_cols=['scores', 'concedes', 'goal_from_shot'])
        Y = self.select_labels(target_cols=self.target_cols)
        self.model_scoring = xgboost.XGBClassifier(
            n_estimators=50, max_depth=3, n_jobs=-1, verbosity=1, enable_categorical=True
        )
        self.model_conceding = xgboost.XGBClassifier(
            n_estimators=50, max_depth=3, n_jobs=-1, verbosity=1, enable_categorical=True
        )
        self.model_scoring.fit(X, Y['scores'])
        self.model_conceding.fit(X, Y['concedes'])

    def predict(self, X_test):
        prob_scores = self.model_scoring.predict_proba(X_test)[:, 1]
        prob_concedes = self.model_conceding.predict_proba(X_test)[:, 1]
        predictions = pd.DataFrame({
            'game_id': self.data.loc[X_test.index, 'game_id'],
            'prob_scores': prob_scores,
            'prob_concedes': prob_concedes
        }, index=X_test.index)
        return predictions
    def _process_single_game(self, game_id, all_predictions, spadl_file_path, output_dir):
        game_preds = all_predictions[all_predictions['game_id'] == game_id]

        # 2. Load the SPADL data for this specific game
        spadl_df = pd.read_parquet(
            spadl_file_path,
            engine='pyarrow',
            filters=[('game_id', '=', game_id)]
        )

        # 3. Merge the probabilities using the shared index
        spadl_df['prob_scores'] = game_preds['prob_scores']
        spadl_df['prob_concedes'] = game_preds['prob_concedes']

        # 4. Calculate VAEP Deltas
        prev_prob_scores = spadl_df['prob_scores'].shift(1, fill_value=0)
        prev_prob_concedes = spadl_df['prob_concedes'].shift(1, fill_value=0)

        spadl_df['offensive_value'] = spadl_df['prob_scores'] - prev_prob_scores
        spadl_df['defensive_value'] = -(spadl_df['prob_concedes'] - prev_prob_concedes)
        spadl_df['vaep_value'] = spadl_df['offensive_value'] + spadl_df['defensive_value']

        # 5. Save the enriched data
        save_path = os.path.join(output_dir, f"spadl_vaep_{game_id}.parquet")
        spadl_df.to_parquet(save_path, engine='pyarrow')
        print(f"  -> Saved: spadl_vaep_{game_id}.parquet")

    def process_all_games(self, all_predictions, spadl_file_path, output_dir):
        """Automatically finds all unique games and processes them."""
        # Automatically detect the games
        unique_games = all_predictions['game_id'].unique()
        print(f"Starting pipeline: Found {len(unique_games)} games to process.")

        # Ensure the output directory exists once
        os.makedirs(output_dir, exist_ok=True)

        # Run the loop internally
        for game_id in unique_games:
            self._process_single_game(game_id, all_predictions, spadl_file_path, output_dir)

        print("Pipeline complete! All games have been enriched with VAEP.")


class xG(Metrics):
    def __init__(self, read_path="../data/game_states", columns=None, filters=None):
        super().__init__(read_path, columns, filters)
        self.target_cols = ['goal_from_shot']
        self.model_goal = None
    def train(self):
        shots_only = self.data[self.data['is_shot'] == 1].copy()
        Y = shots_only['goal_from_shot']
        cols_to_drop = ['scores', 'concedes', 'goal_from_shot', 'is_shot', 'game_id']
        X = shots_only.drop(columns=cols_to_drop)
        self.model_goal = xgboost.XGBClassifier(
            n_estimators=50, max_depth=3, n_jobs=-1, verbosity=1, enable_categorical=True
        )
        self.model_goal.fit(X, Y)
    def predict(self, X_test):
        shot_indices = self.data[self.data['is_shot'] == 1].index
        valid_shot_indices = X_test.index.intersection(shot_indices)
        X_shots = X_test.loc[valid_shot_indices]
        prob_goal = self.model_goal.predict_proba(X_shots)[:, 1]
        predictions = pd.DataFrame({
            'game_id': self.data.loc[valid_shot_indices, 'game_id'],
            'xG': prob_goal,
        }, index=valid_shot_indices)
        return predictions

    def _process_single_game(self, game_id, all_predictions, spadl_file_path, output_dir):
        import os
        import numpy as np

        game_preds = all_predictions[all_predictions['game_id'] == game_id]

        spadl_df = pd.read_parquet(
            spadl_file_path,
            engine='pyarrow',
            filters=[('game_id', '=', game_id)]
        )

        if 'xG' not in spadl_df.columns:
            spadl_df['xG'] = np.nan

        spadl_df.loc[game_preds.index, 'xG'] = game_preds['xG']

        save_path = os.path.join(output_dir, f"spadl_enriched_{game_id}.parquet")
        spadl_df.to_parquet(save_path, engine='pyarrow')
        print(f"  -> Saved xG to: spadl_enriched_{game_id}.parquet")

    def process_all_games(self, all_predictions, spadl_file_path, output_dir):
        import os
        unique_games = all_predictions['game_id'].unique()
        print(f"\nStarting xG Pipeline: Found {len(unique_games)} games to process.")

        os.makedirs(output_dir, exist_ok=True)

        for game_id in unique_games:
            self._process_single_game(game_id, all_predictions, spadl_file_path, output_dir)

        print("xG Pipeline complete! All games have been enriched.")

class PlayerChemistry(Metrics):
    def __init__(self, read_path="../data/spadl", columns=None, filters=None):
        super().__init__(read_path, columns, filters)

    def extended_vaep(self,interaction):
        current_action, next_action = interaction
        return current_action["vaep_value"] + next_action["vaep_value"]

    def get_interactions(self, actions, game_id, player_before, player_after):
        desired_actions = ['receival', 'pass', 'cross', 'dribble', 'take-on', 'shot']

        game_actions = actions[actions['game_id'] == game_id]
        filtered = game_actions[game_actions['type_name'].isin(desired_actions)]

        interactions = []

        for i in range(len(filtered) - 1):
            current_action = filtered.iloc[i]
            next_action = filtered.iloc[i + 1]
            if (current_action["player_id"] == player_before) and (next_action["player_id"] == player_after):
                interactions.append((current_action, next_action))

        return interactions

    def joint_offensive_impact(self,actions, game_id, p, q):
        interactions = self.get_interactions(actions, game_id, p, q)
        interactions_reverse = self.get_interactions(actions, game_id, q, p)
        interactions_sum = 0
        interactions_reverse_sum = 0

        for i in interactions:
            interactions_sum += self.extended_vaep(i)

        for i in interactions_reverse:
            interactions_reverse_sum += self.extended_vaep(i)

        return interactions_sum + interactions_reverse_sum

    def calculate_joi90(self,actions, minutes_df, player1_id, player2_id):
        df_filtered = actions[actions['player_id'].isin([player1_id, player2_id])]
        games_with_x_and_y = (
            df_filtered.groupby('game_id')['player_id']
            .apply(lambda x: set([player1_id, player2_id]).issubset(set(x)))
        )
        selected_games = games_with_x_and_y[games_with_x_and_y].index
        result = actions[actions['game_id'].isin(selected_games)]
        game_ids = result['game_id'].unique().tolist()

        total_joi = 0
        total_minutes = 0

        for game_id in tqdm(game_ids):
            joi_match = self.joint_offensive_impact(actions, game_id, player1_id, player2_id)
            minutes = minutes_df[minutes_df['game_id'] == game_id]['minutes_played'].min()
            if minutes:
                total_joi += joi_match
                total_minutes += minutes

        return (total_joi * 90) / total_minutes if total_minutes else 0

    def actual_offensive_impact(self,actions, player_id, game_id):
        offensive_actions = ['pass', 'cross', 'dribble', 'take-on', 'shot']
        player_actions = actions[(actions['player_id'] == player_id) &
                                 (actions['game_id'] == game_id) &
                                 (actions['type_name'].isin(offensive_actions))]
        return player_actions['vaep_value'].sum()

    def expected_offensive_impact(self,actions, player_id, current_game_id, minutes_df):
        current_game = actions[actions['game_id'] == current_game_id]['game_id'].iloc[0]
        past_games = actions[(actions['player_id'] == player_id) &
                             (actions['game_id'] < current_game)]

        total_minutes = minutes_df[(minutes_df['player_id'] == player_id) &
                                   (minutes_df['game_id'] < current_game)]['minutes_played'].sum()

        if total_minutes == 0:
            return 0.0

        oi_total = 0
        for gid in past_games['game_id'].unique():
            oi_total += self.actual_offensive_impact(actions, player_id, gid)
        return (oi_total * 90) / total_minutes

    def responsibility_share(self, player1_pos, player2_pos, opponent_pos):
        position_map = {
            'GK': (2, 0),
            'RB': (4, 1), 'RWB': (4, 2),
            'CB': (2, 1),
            'LB': (0, 1), 'LWB': (0, 2),
            'CDM': (2, 2), 'DM': (2, 2),
            'CM': (2, 3),
            'CAM': (2, 3.5),
            'RM': (4, 3), 'LM': (0, 3),
            'RW': (4, 4), 'LW': (0, 4),
            'SS': (2, 4.25),
            'CF': (2, 4.5),
            'ST': (2, 5),
            'DF': (2, 1), 'MD': (2, 3), 'FW': (2, 5)
        }

        default_pos = (2, 2)
        pos1 = position_map.get(player1_pos, default_pos)
        pos2 = position_map.get(player2_pos, default_pos)
        opp = position_map.get(opponent_pos, default_pos)

        dist1 = max(euclidean(pos1, opp), 0.1)
        dist2 = max(euclidean(pos2, opp), 0.1)

        return (1 / (dist1 + 1e-5) + 1 / (dist2 + 1e-5)) / 2


def main():
    plotter = Plots(filters = [('game_id', '=', 1914251)])
    plotter.prepare_data(period=2, num_minutes=45, team_name="Real Madrid")
    ax = plotter.draw_pitch()
    plotter.draw_pass_map(
        ax=ax,
        player_position=plotter.player_position,
        player_pass_count=plotter.player_pass_count,
        player_pass_value=plotter.player_pass_value,
        pair_pass_count=plotter.pair_pass_count,
        pair_pass_value=plotter.pair_pass_value,
        title="Passing Network - 1st Half"
    )
    plt.savefig("first_pass_map.png", bbox_inches='tight')
    print("Pitch saved successfully!")
if __name__ == "__main__":
    main()