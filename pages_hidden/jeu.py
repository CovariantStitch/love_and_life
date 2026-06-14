import streamlit as st
import pandas as pd
from pathlib import Path

from pages.jeu_config import start_game_config
from pages.jeu_start import start_game
from utils.data import Game, GameData

# loading CSS
with open("assets/style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# markdown for player cards
st.markdown("""
    <style>
    .players-container {
        display: flex;
        flex-wrap: wrap;
        justify-content: center;
        gap: 32px 24px;
        padding: 24px 0;
        align-items: center;
    }
    .player-card {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 4px 14px rgba(0,0,0,0.1);
        width: 260px;
        text-align: center;
        transition: transform 0.15s;
    }
    .player-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    .avatar-container {
        position: relative;
        height: 180px;
        background: linear-gradient(to bottom, #f1f5f9, #e2e8f0);
    }
    .avatar-icon {
        position: absolute;
        top: 35px;
        left: 50%;
        transform: translateX(-50%);
        width: 100px;
        height: 100px;
        background: #cbd5e1;
        border-radius: 50%;
        border: 5px solid white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 48px;
        color: #475569;
    }
    .gender-badge {
        position: absolute;
        top: 12px;
        left: 12px;
        color: white;
        border-radius: 50%;
        width: 36px;
        height: 36px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        font-weight: bold;
    }
    .menu-dots {
        position: absolute;
        top: 16px;
        right: 16px;
        color: #64748b;
        font-size: 24px;
        cursor: pointer;
    }
    .card-bottom {
        background: #ec4899;
        color: white;
        padding: 20px 16px 16px;
        position: relative;
    }
    .card-bottom::before {
        content: "";
        position: absolute;
        top: -24px;
        left: 0;
        right: 0;
        height: 48px;
        background: #ec4899;
        border-radius: 60% 60% 0 0;
    }
    .player-name {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 6px 0 4px;
        position: relative;
        z-index: 1;
    }
    .player-gender {
        font-size: 1rem;
        opacity: 0.95;
        margin-bottom: 18px;
        position: relative;
        z-index: 1;
    }
    .stats-row {
        display: flex;
        justify-content: space-evenly;
        gap: 12px;
        position: relative;
        z-index: 1;
    }
    .stat-item {
        background: rgba(255,255,255,0.28);
        border-radius: 12px;
        padding: 10px 14px;
        min-width: 70px;
        font-size: 1.1rem;
        font-weight: 600;
    }
    .add-player-card {
        width: 260px;
        height: 380px;
        border: 3px dashed #d1d5db;
        border-radius: 16px;
        background: #f8fafc;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 80px;
        color: #9ca3af;
        cursor: pointer;
        transition: all 0.2s;
    }
    .add-player-card:hover {
        border-color: #ec4899;
        color: #ec4899;
        background: #fdf2f8;
        transform: scale(1.04);
    }
    </style>
""", unsafe_allow_html=True)

if 'game' not in st.session_state:
    st.session_state.game = Game()
    if st.session_state.is_local:
        st.session_state.df_game_data = pd.read_csv(Path(__file__).parent / "resources" / "game.csv").dropna(axis=1, how="all")
    else:
        st.session_state.df_game_data = st.session_state.gsheets_connection.read(worksheet="game")
    st.session_state.game_data = GameData(st.session_state.df_game_data)

if "game_started" not in st.session_state:
    st.session_state.game_started = False

if st.session_state.game_started is False:
    start_game_config()
else:
    st.session_state.game.start()
    start_game()
