# tf2-2024-wrap-up
Some cool data visualization for competitive tf2 in 2024.

## setup for development
This is very much still a work in progress and not ready for actual deployment. Setup instructions reflect use in a dev environment by some sort of monkey (me)
### setup python:
setup the environment
`python -m venv venv`
`source venv/bin/activate`

install requirements:
`pip install -r requirements.txt`
### *optional* get dataset:
one for most of 2024 is already provided in data/log_dumps/
`python scripts/get_logs.py -sd *date* -ed *date* -p *folder to dump data*`
### build the database:
`python scripts/build_db.py -i data/log_dumps/`

### *optional* populate player names:
If you are using the existing dataset, use the `--csv data/name_map.csv` option first, then fill in gaps if needed.
`python scripts/populate_names.py --csv`
### generate a graph:
*WIP*
parse_logs.py still works if you need nodes and edges, but the rewrite using the sqlite db is under construction.
probably finished tomorrow tbh
generating nodes and edges for use in Gephi will look like:
`python scripts/make_graph.py --name sixes_data_for_gephi --format sixes -min 5 --csv`
precomputing the whole graph for direct use on the frontend:
`python scripts/make_graph.py --name sixes_graph --format sixes -min 5 --json --precompute --modularity 1`
### start backend
This is not where this should live and is moving don't judge me
`flask --app scripts/api.py run --debug`
### start frontend
Also just wildly WIP. Full rewrite underway, kinda just a technical proof of concept at the moment.
`cd frontend`
`npm install`
`npm run dev --debug