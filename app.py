from flask import Flask, render_template, request
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

app = Flask(__name__)

# Load the dataset
cyber_df = pd.read_csv("Global_Cybersecurity_Threats_2015-2024.csv")
years = sorted(cyber_df["Year"].unique(), reverse=True)

def generate_graphs(year):
    data_year = cyber_df[cyber_df["Year"] == int(year)]

    # 1. Top 5 Countries by Financial Loss
    top5_loss = data_year.groupby("Country")["Financial Loss (in Million $)"].sum().nlargest(5).reset_index()
    fig_loss = px.bar(top5_loss, x="Country", y="Financial Loss (in Million $)",
                      title="Top 5 Countries by Financial Loss", color_discrete_sequence=["#1909f7"])

    # 2. Most Common Attack Types (Pie)
    attack_counts = data_year["Attack Type"].value_counts().nlargest(5).reset_index()
    attack_counts.columns = ["Attack Type", "Count"]
    fig_attacks = px.pie(attack_counts, names="Attack Type", values="Count",
                         title="Most Common Attack Types", hole=0.4)

    # 3. Most Targeted Industries (Treemap)
    fig_industry = px.treemap(data_year, path=['Target Industry'],
                              title="Top Targeted Industries (Treemap)")

    # 4. Attack Sources (Horizontal Bar)
    source_counts = data_year["Attack Source"].value_counts().nlargest(5).reset_index()
    source_counts.columns = ["Source", "Count"]
    fig_sources = px.bar(source_counts, x="Count", y="Source", orientation='h',
                         title="Top Attack Sources", color_discrete_sequence=["#1909f7"])

    # 5. Average Resolution Time by Country (Line)
    res_time = data_year.groupby("Country")["Incident Resolution Time (in Hours)"].mean().nlargest(5).reset_index()
    fig_res_time = px.line(res_time, x="Country", y="Incident Resolution Time (in Hours)",
                           markers=True, title="Avg Resolution Time by Country")

    # 6. Users Affected by Country (Bubble Chart)
    affected = data_year.groupby("Country")["Number of Affected Users"].sum().nlargest(5).reset_index()
    fig_affected = px.scatter(affected, x="Country", y="Number of Affected Users",
                              size="Number of Affected Users", color="Country",
                              title="Users Affected by Country (Bubble Chart)")

    return [fig.to_html(full_html=False) for fig in [
        fig_loss, fig_attacks, fig_industry, fig_sources, fig_res_time, fig_affected
    ]]

@app.route("/")
def index():
    year = request.args.get("year", str(years[0]))
    graphs = generate_graphs(year)
    return render_template("index.html", graphs=graphs, years=years, selected_year=int(year))

if __name__ == "__main__":
    app.run(debug=True)
