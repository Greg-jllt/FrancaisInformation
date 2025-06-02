import altair as alt
import pandas as pd


import altair as alt
import pandas as pd


def make_donut(input_response, input_text, input_color, legend_labels, legend_order):
    if input_color == "blue":
        chart_color = ["#155F7A", "#29b5e8"]
    if input_color == "green":
        chart_color = ["#12783D", "#27AE60"]
    if input_color == "orange":
        chart_color = ["#F39C12", "#875A12"]
    if input_color == "red":
        chart_color = ["#781F16", "#E74C3C"]
    if input_color == "bleu ciel":
        chart_color = ["#5DADE2", "#2E86C1"]
    if input_color == "jaune":
        chart_color = ["#F1C40F", "#F39C12"]
    if input_color == "rose":
        chart_color = ["#F1948A", "#EC7063"]
    if input_color == "violet":
        chart_color = ["#BB8FCE", "#8E44AD"]
    if input_color == "vert clair":
        chart_color = ["#27AE60", "#82E0AA"]

    # Utiliser les étiquettes personnalisées pour la légende
    source = pd.DataFrame(
        {"Topic": legend_labels, "% value": [100 - input_response, input_response]}
    )
    source_bg = pd.DataFrame({"Topic": legend_labels, "% value": [100, 0]})

    plot = (
        alt.Chart(source)
        .mark_arc(innerRadius=45, cornerRadius=25)
        .encode(
            theta="% value",
            color=alt.Color(
                "Topic:N",
                scale=alt.Scale(
                    domain=legend_order,  # Spécifier l'ordre des étiquettes
                    range=chart_color,
                ),
                legend=alt.Legend(title=""),  # Légende avec étiquettes personnalisées
            ),
        )
        .properties(width=130, height=130)
    )

    text = plot.mark_text(
        align="center",
        color="white",
        font="Lato",
        fontSize=32,
        fontWeight=700,
        fontStyle="italic",
    ).encode(text=alt.value(f"{input_response} %"))
    
    plot_bg = (
        alt.Chart(source_bg)
        .mark_arc(innerRadius=45, cornerRadius=20)
        .encode(
            theta="% value",
            color=alt.Color(
                "Topic:N",
                scale=alt.Scale(
                    domain=legend_order,  # Spécifier l'ordre des étiquettes
                    range=[chart_color[1], chart_color[0]],
                ),
            ),
        )
        .properties(width=130, height=130)
    )

    # Ajouter un titre global au graphique
    final_chart = (plot_bg + plot + text)

    return final_chart