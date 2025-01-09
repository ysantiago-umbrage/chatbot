from openai import OpenAI
import psycopg2

client = OpenAI(
	api_key = "OpenAI_Key_Here"
)

def call_chat_gpt(prompt):
	response = client.chat.completions.create(
		model = "gpt-3.5-turbo",
		messages = [{"role": "user", "content": prompt}]
	)

	return response.choices[0].message.content.strip()


def embed_text(str):
    response = client.embeddings.create(
        model = "text-embedding-3-small",
        input = str,
        encoding_format = "float"
    )

    return response.data[0].embedding


def query(embedding):
	connection_str = "dbname='vector_db' user='postgres' host='localhost' password='password'"

	conn = psycopg2.connect(connection_str)
	cursor = conn.cursor()

	query = f"""SELECT id, history, 1 - cosine_distance(embedding, vector('{embedding}')) AS cosine_similarity
               FROM test
               ORDER BY cosine_similarity DESC LIMIT 3;"""

	cursor.execute(query)

	columns = list(cursor.description)

	rows = cursor.fetchall()

	results = []

	for row in rows:
		row_dict = {}
		for i, column in enumerate(columns):
			row_dict[column.name] = row[i]
			results.append(row_dict)
	
	return results[0]['history']

if __name__ == "__main__":
	while True:
		user_input = input("\nYou: ")
		if user_input.lower() in ["quit", "exit"]:
			break

		embedding = embed_text(user_input)

		response = query(embedding)

		print("\nChatbot: ", response)
