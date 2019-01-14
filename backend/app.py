from flask_graphql import GraphQLView
import graphene
from flask_cors import CORS
from schema import Mutation, Query
from utils import app, db

CORS(app)
schema = graphene.Schema(query=Query, mutation=Mutation)

# Basic GraphQL set-up
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True
    )
)


@app.route('/')
def index():
    welcome_header = '<h1>Welcome to the back-end REST API of the tech cabinet rental platform!</h1>'
    graphql_endpoint = '<p>To use this API, visit the GraphQL end-point: <a href="http://127.0.0.1:5000/graphql">/graphql</a></p>'
    return welcome_header + graphql_endpoint


if __name__ == '__main__':
     app.run()

