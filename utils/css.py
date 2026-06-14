def custom_container(container_id: str, container_color: str) -> str:
    css = f"""
        <style>
            /* Cible uniquement CE container */
            div.st-key-{container_id} {{
                background-color: {container_color};
                border-radius: 12px;
                padding: 1.2rem;
                margin-bottom: 1.5rem;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
                border: 1px solid #e8ecef;
                transition: box-shadow 0.2s;
            }}
            div.st-key-{container_id}:hover {{
                box-shadow: 0 6px 16px rgba(0,0,0,0.15);
            }}
            div.st-key-{container_id} .stCheckbox {{
                margin-top: 0.8rem;
            }}
            div.st-key-{container_id} .stTextInput > div > div > input {{
                border-radius: 6px;
            }}
        </style>
        """
    return css

def custom_button(color1: str="#ec4899", color2: str="#db2777"):
    # careful here, this overdefines the streamlit usual buttons
    # there is a better way to proceed: going trough st.components.v2 and building a new button
    #todo: convert all the call to this function to st.components.v2
    css_button = f"""
        <style>
            div[data-testid="stButton"] > button[kind="primary"] {{
                background: linear-gradient(135deg, {color1}, {color2});
                color: white;
                border: none;
                border-radius: 8px; 
                padding: 0.65rem 1.4rem;
                font-size: 1rem;
                font-weight: 500;
                letter-spacing: 0.3px;
                transition: all 0.2s ease;
                box-shadow: 0 2px 6px rgba(44, 123, 229, 0.2);
            }}
    
            div[data-testid="stButton"] > button[kind="primary"]:hover {{
                background: linear-gradient(135deg, #f089bc, #ec4899);
                box-shadow: 0 4px 12px rgba(44, 123, 229, 0.3);
                transform: translateY(-3px);
            }}
            
            div[data-testid="stButton"] > button[kind="primary"]:active {{
            transform: translateY(0);
            box-shadow: 0 2px 4px rgba(44, 123, 229, 0.25);
            }}
    
            div[data-testid="stButton"] > button[kind="primary"]:focus {{
                box-shadow: none !important;
            }}
            
            div[data-testid="stButton"] > button[kind="primary"]:disabled,
            div[data-testid="stButton"] > button[kind="primary"]:disabled:hover,
            div[data-testid="stButton"] > button[kind="primary"]:disabled:active {{
                background: linear-gradient(135deg, #d4a5c4, #c084a6) !important;
                color: #f8e8f0 !important;
                opacity: 0.75;
                cursor: not-allowed;
                box-shadow: none !important;
                transform: none !important;
            }}
        </style>
        """
    return css_button

def custom_card_add():
    #todo: find a way to generalize the st.components.v2 used in different routines
    pass

def task_card(name: str, overdue: bool, due_text: str, points: int|None, description: str|None):
    name_css = f'<div class="task-name">{name}</div>'

    if overdue:
        time_css = f'<span class="overdue">{due_text} · En retard</span>'
    else:
        time_css = f'<div class="task-meta">Échéance : {due_text}</div>'

    if points is not None:
        points_css = f'<div class="task-meta">Points : {points}</div>'
    else:
        points_css = ""

    if description is not None:
        description_css = f'<div class="task-description">{description}</div>'
    else:
        description_css = ''

    dots_css = f"<div class='task-dots'>...</div>"

    return name_css + time_css + points_css + description_css + dots_css

