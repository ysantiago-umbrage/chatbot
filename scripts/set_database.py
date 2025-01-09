import psycopg2
from openai import OpenAI


client = OpenAI(
	api_key = "OpenAI_Key_Here"
)


def main():
    create_vector_if_not_exists()

    create_table_if_not_exists()

    results = get_table_data()

    data = embed_data(results)

    for item in data:
        update_table_data(item['id'], item['embedding'])


def create_table_if_not_exists():
    connection_str = "dbname='vector_db' user='postgres' host='localhost' password='password'"
    conn = psycopg2.connect(connection_str)
    cursor = conn.cursor()
    
    cursor.execute("CREATE TABLE IF NOT EXISTS test (id integer PRIMARY KEY, name varchar(200), history varchar(10000), embedding vector(1536));")

    conn.commit()


def create_vector_if_not_exists():
    connection_str = "dbname='vector_db' user='postgres' host='localhost' password='password'"
    conn = psycopg2.connect(connection_str)
    cursor = conn.cursor()
    
    cursor.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    conn.commit()


def get_table_data():
    connection_str = "dbname='vector_db' user='postgres' host='localhost' password='password'"
    conn = psycopg2.connect(connection_str)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, history FROM test WHERE embedding IS NULL ;")

    columns = list(cursor.description)

    rows = cursor.fetchall()

    results = []

    for row in rows:
        row_dict = {}
        for i, column in enumerate(columns):
            row_dict[column.name] = row[i]
        results.append(row_dict)

    return results


def update_table_data(id, embedding):
    connection_str = "dbname='vector_db' user='postgres' host='localhost' password='password'"
    conn = psycopg2.connect(connection_str)
    cursor = conn.cursor()
    
    query = """UPDATE test SET embedding = %s WHERE id = %s;"""

    cursor.execute(query, (embedding, id))

    conn.commit()


def embed_data(results):
    data = []

    for item in results:
        embedding = embed_text(item['history'])
        item['embedding'] = embedding
        data.append(item)
    
    return data

def embed_text(str):
    response = client.embeddings.create(
        model = "text-embedding-3-small",
        input = str,
        encoding_format = "float"
    )

    return response.data[0].embedding


if __name__ == '__main__':
    print("Testing db")
    main()
