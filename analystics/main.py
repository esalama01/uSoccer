from data_analysis import VAEP, Plots
import matplotlib.pyplot as plt


def main():
    print("--- STARTING VAEP ML PIPELINE ---")

    # 1. Initialize the VAEP model with your game states data
    print("[1/4] Loading game states and initializing VAEP...")
    vp = VAEP(read_path="../data/game_states")

    # 2. Train the XGBoost models
    print("[2/4] Training scoring and conceding models...")
    vp.train()

    # 3. Extract features and predict probabilities
    print("[3/4] Predicting VAEP probabilities...")
    X_features = vp.select_features()  # Fixed: No arguments passed here!
    predictions = vp.predict(X_features)

    # 4. Calculate final VAEP and save to a NEW enriched folder
    print("[4/4] Enriching SPADL data with VAEP values...")
    vp.process_all_games(
        all_predictions=predictions,
        spadl_file_path="../data/spadl",  # Read the raw SPADL
        output_dir="../data/spadl_enriched"  # Save the enriched data here
    )

    print("\n--- GENERATING PASSING NETWORK ---")

    # 5. Initialize Plots using the ENRICHED data path
    # Pointing to spadl_enriched ensures it finds the new 'vaep_value' column
    print("Plotting passing network...")
    plotter = Plots(
        read_path="../data/spadl_enriched",
        filters=[('game_id', '=', 1821496)]
    )

    plotter.prepare_data(period=2, num_minutes=45, team_name="Barcelona")
    ax = plotter.draw_pitch()

    plotter.draw_pass_map(
        ax=ax,
        player_position=plotter.player_position,
        player_pass_count=plotter.player_pass_count,
        player_pass_value=plotter.player_pass_value,
        pair_pass_count=plotter.pair_pass_count,
        pair_pass_value=plotter.pair_pass_value,
        title="Barcelona - VAEP Passing Network (2nd Half)"
    )

    plt.savefig("first_pass_map.png", bbox_inches='tight')
    print("✅ Pitch saved successfully to first_pass_map.png!")


if __name__ == "__main__":
    main()