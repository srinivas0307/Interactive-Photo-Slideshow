from flask import Flask, request, jsonify, render_template, redirect, flash, url_for, session, Response
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
import psycopg2.extras
from PIL import Image
import os
import io
import json
import base64
import shutil
import tempfile
from urllib.parse import urlparse
from moviepy.editor import AudioFileClip, concatenate_audioclips, ImageSequenceClip

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 's_j_b')
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET', 'project_k')
jwt = JWTManager(app)

# db connection for render
def get_db_connection():
    # Parse the DATABASE_URL
    url = urlparse(os.environ["DATABASE_URL"])

    # Decode the base64 certificate
    cert_decoded = base64.b64decode(os.environ['ROOT_CERT_BASE64'])

    # Define the path to save the certificate
    cert_path = '/opt/render/.postgresql/root.crt'
    os.makedirs(os.path.dirname(cert_path), exist_ok=True)

    # Write the certificate to the file
    with open(cert_path, 'wb') as cert_file:
        cert_file.write(cert_decoded)

    # Set up the connection string with the path to the certificate
    conn = psycopg2.connect(
        host=url.hostname,
        port=url.port,
        dbname=url.path[1:],
        user=url.username,
        password=url.password,
        sslmode='verify-full',
        sslrootcert=cert_path
    )
    return conn

# Configure PostgreSQL connection

# def get_db_connection():
#  # Connect to the PostgreSQL database using the DATABASE_URL from
#     return psycopg2.connect(os.environ["DATABASE_URL"])

# Routes

@app.route('/')
def show():
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('show'))

@app.route('/profile')
def profile():
    # Retrieve user data from the session or database
    user_id = session.get('user_id')
    if user_id:
        connection = get_db_connection()
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            sql = "SELECT username, email ,user_id FROM users WHERE user_id=%s"
            cursor.execute(sql, (user_id,))
            user = cursor.fetchone()
        # Fetch user data based on user_id
        # Example: user_data = fetch_user_data_from_database(user_id)
        return jsonify(user), 200
    else:
        return jsonify({'error': 'User not logged in'}), 401  # Unauthorized


@app.route('/remake')
def remake():
    return render_template('index.html')

def admin_panel():
    try:
        connection = get_db_connection()
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # Fetch all user data from the database
            cursor.execute("SELECT user_id, username, email FROM users")
            users_data = cursor.fetchall()

            # Close the database connection
            connection.close()

            # Render the admin.html template with the user data
            return render_template('admin.html', users=users_data)
    except Exception as e:
        # Handle exceptions
        app.logger.error(f"Error fetching users data: {str(e)}")
        flash(f"An unexpected error occurred: {str(e)}", 'error')
        return redirect(url_for('show'))  # Redirect to the appropriate page


@app.route('/login', methods=['POST'])
def login():
    data = request.form
    username = data.get('txt')
    password = data.get('pswd')
    
    if username == 'admin' and password == 'admin':
        return admin_panel()
    
    try:
        connection = get_db_connection()
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            sql = "SELECT username, password,user_id FROM users WHERE username=%s"
            cursor.execute(sql, (username,))
            user = cursor.fetchone()
            if user and check_password_hash(user['password'], password):
                # Store password in the JWT token (for educational purposes only)
                access_token = create_access_token(identity=username, additional_claims={'password': password})
                session['user_id'] = user['user_id']
                flash(f"Login successful. Welcome back, {username}!", 'success')
                return render_template('index.html', access_token=access_token)
            else:
                flash("Invalid username or password", 'error')
                return redirect(url_for('show'))
    except Exception as e:
        app.logger.error(f"Error during login: {str(e)}")
        flash(f"An unexpected error occurred: {str(e)}", 'error')
        return redirect(url_for('show'))
    finally:
        connection.close()

@app.route('/signup', methods=['POST'])
def signup():
    data = request.form
    username = data.get('txt')
    email = data.get('email')
    password = data.get('pswd')

    try:
        connection = get_db_connection()
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            sql_check = "SELECT username FROM users WHERE username=%s OR email=%s"
            cursor.execute(sql_check, (username, email))
            existing_user = cursor.fetchone()

            if existing_user:
                flash("Username or email already exists", 'error')
                return redirect(url_for('show'))

            hashed_password = generate_password_hash(password)

            sql_insert = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(sql_insert, (username, email, hashed_password))
            connection.commit()

            flash(f"Account created successfully. Welcome, {username}!", 'success')
            return redirect(url_for('show'))
    except Exception as e:
        app.logger.error(f"Error during signup: {str(e)}")
        flash(f"An unexpected error occurred: {str(e)}", 'error')
        return redirect(url_for('show'))
    finally:
        connection.close()


@app.route('/upload_images', methods=['POST'])
def upload_images():
    try:
        connection = get_db_connection()
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # Create a table to store images if not exists
            # cursor.execute("CREATE TABLE IF NOT EXISTS images (id SERIAL PRIMARY KEY, user_id INT, metadata JSON, image_data BYTEA, FOREIGN KEY (user_id) REFERENCES users(user_id))")
            
            # Retrieve uploaded images
            uploaded_images = request.files.getlist('images')
            
            for image in uploaded_images:
                # Read image data
                image_data = image.read()

                # Example: Extract metadata (replace this with your actual metadata extraction logic)
                metadata = {'filename': image.filename, 'size': len(image_data)}

                # Log relevant information before attempting to insert into the database
                app.logger.info(f"Uploading image: {metadata}")
                
                try:
                    # Get user_id from the current user
                    user_id = session.get('user_id')

                    # Insert image data, user_id, and metadata into the database
                    cursor.execute("INSERT INTO images (user_id, metadata, image_data) VALUES (%s, %s, %s)", (user_id, json.dumps(metadata), image_data))

                    # Commit changes to the database
                    connection.commit()
                    flash("Images uploaded successfully", 'success')
                except Exception as upload_error:
                    # Log the error and relevant information
                    app.logger.error(f"Error during image upload: {str(upload_error)}")
                    app.logger.error(f"Failed to upload image: {metadata}")
                    flash(f"An unexpected error occurred during image upload", 'error')
                    continue
    except Exception as e:
        app.logger.error(f"Error during image upload: {str(e)}")
        flash(f"An unexpected error occurred: {str(e)}", 'error')
    finally:
        if connection:
            connection.close()

    return render_template('index.html')



@app.route('/retrieve_images', methods=['GET'])
def retrieve_images():
    try:
        # Get user_id from the current user
        user_id = session.get('user_id')

        connection = get_db_connection()
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            # Retrieve images for the user
            cursor.execute("SELECT metadata, image_data FROM images WHERE user_id = %s", (user_id,))
            images_data = cursor.fetchall()

            # Create a list to store image information
            images = []
            for image_data in images_data:
                # Append image metadata and base64-encoded data to the list
                image = {
                    'metadata': image_data['metadata'],
                    'image_data': base64.b64encode(image_data['image_data']).decode('utf-8')
                }

                # Add a checkbox input for each image
                image['checkbox'] = f'<input type="checkbox" class="image-checkbox" value="{image["image_data"]}" data-filename="{image["metadata"]["filename"]}">'

                # Append the image to the list
                images.append(image)

            return jsonify(images), 200

    except Exception as e:
        app.logger.error(f"Error during image retrieval: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred during image retrieval'}), 500

    finally:
        if connection:
            connection.close()

def retrieve_audio_data(audio_id):
    print(audio_id)
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT BlobData FROM AudioFiles WHERE id = %s", (int(audio_id),))
            audio_data = cursor.fetchone()

            if audio_data:
                audio_data = audio_data[0]
                return audio_data  # Return audio data directly

            return None  # Return None if audio track not found

    except Exception as e:
        app.logger.error(f"Error during audio track retrieval: {str(e)}")
        return None

    finally:
        if connection:
            connection.close()


# Route to retrieve all audio tracks
@app.route('/retrieve_audio_tracks', methods=['GET'])
def retrieve_audio_tracks():
    try:
        connection = get_db_connection()
        with connection.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute("SELECT id, file_name FROM AudioFiles")
            audio_tracks = cursor.fetchall()
            print(audio_tracks)
            return jsonify(audio_tracks), 200

    except Exception as e:
        app.logger.error(f"Error during audio track retrieval: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred during audio track retrieval'}), 500

    finally:
        if connection:
            connection.close()

# Route to retrieve a specific audio track by ID
import io

@app.route('/retrieve_audio_track/<int:audio_id>', methods=['GET'])
def retrieve_audio_track(audio_id):
    print(audio_id)
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            cursor.execute("SELECT BlobData FROM AudioFiles WHERE id = %s", (int(audio_id),))
            audio_data = cursor.fetchone()

            if audio_data:
                audio_data = audio_data[0]  # Assuming BlobData is the first element in the tuple
                return Response(io.BytesIO(audio_data), mimetype='audio/mpeg')  # Return audio data as Response

            return '', 404  # Return 404 if audio track not found

    except Exception as e:
        app.logger.error(f"Error during audio track retrieval: {str(e)}")
        return '', 500  # Return 500 for internal server error

    finally:
        if connection:
            connection.close()



@app.route('/create_slideshow_video', methods=['POST'])
def create_slideshow():
    try:
        # Retrieve selected audio ID and images from the form data
        selected_audio_id = request.form.get('selectedAudioId')
        selected_images_json = request.form.get('selectedImages')
        selected_duration = request.form.get('selectedduration')
        selected_transition = request.form.get('selectedtransition')
        selected_resolution = request.form.get('selectedResolution')
        video_quality = request.form.get('videoQuality')
        # print("images are",selected_images_json
        # Parse the selected images JSON string to a Python list
        selected_images = json.loads(selected_images_json)

        # Retrieve the selected audio data based on the selected_audio_id
        selected_audio_data = retrieve_audio_data(selected_audio_id)
        print('selected resolution', selected_resolution)
        # Use the create_slideshow_video function to generate the video
        output_video_path = create_slideshow(selected_images, selected_audio_data, selected_duration,
                                             selected_resolution, selected_transition, video_quality)

        # Return the output video path or any other relevant information
        return render_template('preview.html')

    except Exception as e:
        app.logger.error(f"Error creating slideshow video: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred during video creation'}), 500


def create_slideshow(images, audio_data, duration, resolution, transition_effect, quality):
    # Create a temporary directory to store image and audio files
    temp_dir = tempfile.mkdtemp()

    # Initialize a list to store video frames and image durations
    output_dir = 'static/videos'
    output_path = os.path.join(output_dir, 'output_video.mp4')
    video_frames = []
    image_durations = []
    resolution_mapping = {'480p': (854, 480), '720p': (1280, 720), '1080p': (1920, 1080)}

    # Determine width and height based on resolution
    width, height = resolution_mapping.get(resolution, (1280, 720))

    # Quality mapping
    quality_mapping = {'low': 1, 'medium': 10, 'high': 20}
    quality_factor = quality_mapping.get(quality, 8)  # Default to medium quality

    try:
        # Process each selected image
        for i, image_info in enumerate(images):
            image_data = image_info['imageData']
            image_duration = image_info.get('duration', int(duration))

            # Convert base64 image data to a format compatible with Pillow
            image = Image.open(io.BytesIO(base64.b64decode(image_data)))

            # Convert the image to RGB mode (remove alpha channel)
            image = image.convert('RGB')

            # Resize image to specified resolution
            resized_image = image.resize((width, height))

            # Save the resized image to a temporary file
            image_path = os.path.join(temp_dir, f'temp_image_{i}.jpg')
            resized_image.save(image_path)

            # Add the image to the video frames and store its duration
            video_frames.append(image_path)
            image_durations.append(image_duration)

        if audio_data is not None:
            # Save the audio data to a temporary file
            audio_file_path = os.path.join(temp_dir, 'temp_audio.mp3')
            with open(audio_file_path, 'wb') as audio_file:
                audio_file.write(audio_data)

            # Calculate the total duration of the slideshow
            total_duration = sum(image_durations)

            # Load the selected audio data as an audio clip
            audio_clip = AudioFileClip(audio_file_path)

            # Determine how many times to repeat the audio to match the total duration
            num_repeats = int(total_duration / audio_clip.duration) + 1

            # Repeat the audio as needed
            repeated_audio_clip = concatenate_audioclips([audio_clip] * num_repeats)

            # Create an ImageSequenceClip from the list of image paths with specified durations
            video_clip = ImageSequenceClip(video_frames, durations=image_durations, fps=1 / int(duration))

            # Set the audio of the video clip with repeated audio
            video_clip = video_clip.set_audio(repeated_audio_clip)

            # Set the total duration of the video clip
            video_clip = video_clip.set_duration(total_duration)

            # Write the final video to the specified output path with specified quality
            video_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', bitrate=f"{quality_factor}M")
            video_clip.close()

            # Return the output path or any other relevant information
            return output_path
        else:
            return "Audio track not found", 404
    finally:
        # Clean up temporary files and directory
        shutil.rmtree(temp_dir)


@jwt_required()
@app.route('/protected')
def protected():
    current_user = get_jwt_identity()
    password = request.jwt_claims.get('password')
    return jsonify(logged_in_as=current_user, password=password), 200

if __name__ == '__main__':
    app.run(debug=True, port=7000)
