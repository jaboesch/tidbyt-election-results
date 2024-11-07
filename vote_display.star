load("render.star", "render")
load("http.star", "http")
load("encoding/json.star", "json")

# URL of the Flask server running the scrape_vote_count script
API_URL = "http://127.0.0.1:5000/api/election"

def get_data(url):
    res = http.get(url, ttl_seconds=30)
    if res.status_code != 200:
        fail("GET %s failed with status %d: %s", url, res.status_code, res.body())
    return res.json()

def main():
    # Fetch election data from the API
    data = get_data(API_URL)
    print(data)

    # Extract the candidate names and their respective votes
    dem_votes = data.get("dem", "N/A")
    gop_votes = data.get("gop", "N/A")
    timestamp = data.get("timestamp", "N/A")

    # Calculate proportions for a 270-bar
    # Ensure that votes are integers for calculation
    dem_votes = int(dem_votes)
    gop_votes = int(gop_votes)
    dem_proportion = min(dem_votes / 270.0, 1.0)
    gop_proportion = min(gop_votes / 270.0, 1.0)

    return render.Root(
        child=render.Column(
            main_align="center",
            cross_align="center",
            expanded=True,
            children=[    
                render.Box(
                    height=6,
                    padding=1,
                    child=render.Row(
                        main_align="space_between",
                        cross_align="space_between",
                        expanded=True,
                        children=[
                            render.Box(width=int(dem_proportion * 30), height=4, color="#0000FF"),
                            render.Box(width=int(gop_proportion * 30), height=4, color="#FF0000"),
                        ]
                    )
                ),

                render.Row(
                    main_align="space_evenly",
                    cross_align="center",
                    expanded=True,
                    children=[
                        render.Text(str(dem_votes), color="#0000FF", font="10x20"),
                        render.Text(str(gop_votes), color="#FF0000", font="10x20"),
                    ]
                )
            ],
        ),
    )
