import streamlit as st
import pickle
import requests
import hashlib
import mysql.connector



def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to create a MySQL database connection
def create_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="xxxxxx",
        database="Project"
    )
    cursor = conn.cursor()
    return conn, cursor

# Function to initialize the user table
def init_user_table(cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS User (
            UserID INT AUTO_INCREMENT PRIMARY KEY,
            Username VARCHAR(50) NOT NULL UNIQUE,
            Password VARCHAR(255) NOT NULL
        )
    """)
    conn.commit()

# Function to check login credentials
def check_login(username, hashed_password):
    cursor.execute("SELECT * FROM User WHERE Username = %s AND Password = %s", (username, hashed_password))
    user = cursor.fetchone()
    return user

# Function to get user ID based on username
def get_user_id(username):
    cursor.execute("SELECT UserID FROM User WHERE Username = %s", (username,))
    user_id = cursor.fetchone()
    return user_id[0] if user_id else None

# Function to register a new user
def register_user(username, password):
    hashed_password = hash_password(password)
    cursor.execute("INSERT INTO User (Username, Password) VALUES (%s, %s)", (username, hashed_password))
    conn.commit()

# Create or connect to the MySQL database
conn, cursor = create_connection()

# Initialize the User table
init_user_table(cursor)




if st.session_state.get('logged_in', False):
    # Rest of your code for movie recommendation system
    def fetch_poster(movie_id):
        url = "https://api.themoviedb.org/3/movie/{}?api_key=c7ec19ffdd3279641fb606d19ceb9bb1&language=en-US".format(movie_id)
        data=requests.get(url)
        data=data.json()
        poster_path = data['poster_path']
        full_path = "https://image.tmdb.org/t/p/w500/"+poster_path
        return full_path

    movies = pickle.load(open("movies_list.pkl", 'rb'))
    similarity = pickle.load(open("similarity.pkl", 'rb'))
    movies_list=movies['title'].values

    st.header("Movie Recommender System")

    import streamlit.components.v1 as components
    
    imageCarouselComponent = components.declare_component("image-carousel-component", path="frontend/public")


    imageUrls = [
        fetch_poster(1632),
        fetch_poster(299536),
        fetch_poster(17455),
        fetch_poster(429422),
        fetch_poster(9722),
        fetch_poster(240),
        fetch_poster(155),
        fetch_poster(598)
    
        ]


    imageCarouselComponent(imageUrls=imageUrls, height=200)


    selectvalue=st.selectbox("Select movie from dropdown", movies_list)

    def recommend(movie):
        index=movies[movies['title']==movie].index[0]
        distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector:vector[1])
        recommend_movie=[]
        recommend_poster=[]
        for i in distance[1:6]:
            movies_id=movies.iloc[i[0]].id
            recommend_movie.append(movies.iloc[i[0]].title)
            recommend_poster.append(fetch_poster(movies_id))
        return recommend_movie, recommend_poster



    if st.button("Show Recommendations"):
        movie_name, movie_poster = recommend(selectvalue)
        col1,col2,col3,col4,col5=st.columns(5)
        with col1:
            st.text(movie_name[0])
            st.image(movie_poster[0])
        with col2:
            st.text(movie_name[1])
            st.image(movie_poster[1])
        with col3:
            st.text(movie_name[2])
            st.image(movie_poster[2])
        with col4:
            st.text(movie_name[3])
            st.image(movie_poster[3])
        with col5:
            st.text(movie_name[4])
            st.image(movie_poster[4])

    if st.button("Logout"):
        st.session_state.logged_in = False

    # User registration section
else:
    st.subheader('Login or Sign Up')
    st.subheader('Select Action')
    login_or_signup = st.radio("Choose an option:", ("Login", "Sign Up"))

    # Sign Up Section
    if login_or_signup == "Sign Up":
        st.subheader('Sign Up')
        new_username = st.text_input('Username')
        new_password = st.text_input('Password', type='password')

        if st.button('Sign Up'):
            if new_username and new_password:
                # Check if the username is already taken
                cursor.execute("SELECT * FROM User WHERE Username = %s", (new_username,))
                existing_user = cursor.fetchone()

                if existing_user:
                    st.error('Username already taken. Please choose a different one.')
                else:
                    # Insert new user into UserDB
                    register_user(new_username, new_password)
                    st.success('Sign Up successful! You can now log in.')
            else:
                st.error('Please fill in all the fields for Sign Up.')

    # Login Section
    if login_or_signup == "Login":
        st.subheader('Login')
        username = st.text_input('Username')
        password = st.text_input('Password', type='password')

        if st.button('Login'):
            if username and password:
                user = check_login(username, password)

                if user:
                    st.success('Login successful!')
                    st.session_state.logged_in = True
                    st.session_state.user_id = get_user_id(username)  # Fetch user_id based on the username
                else:
                    st.error('Invalid username or password')

# Close the database connection
conn.close()
