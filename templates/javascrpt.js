createSlideshowButton.addEventListener('click', createSlideshow);


function createSlideshow() {
    // Check if there are images to create a slideshow
    if (selectedImages.length === 0) {
        alert('Please select images first.');
        return;
    }

    // Get other customization options
    const imageDuration = parseInt(document.getElementById('imageDuration').value, 10) || 5; // Default duration is 5 seconds
    const transitionEffect = document.getElementById('transitionEffect').value;

    // Get selected background music
    const backgroundMusicInput = document.getElementById('backgroundMusic');
    const selectedMusic = backgroundMusicInput.files[0];

    // Create slideshow container
    const slideshowContainer = document.createElement('div');
    slideshowContainer.classList.add('slideshow-container');

    // Create slides with selected images
    selectedImages.forEach((imageSrc, index) => {
        console.log(`Image ${index + 1}: ${imageSrc}`);
        const slide = document.createElement('div');
        slide.classList.add('mySlides');
        slide.style.display = index === 0 ? 'block' : 'none'; // Show the first slide, hide others

        // Create image element within the slide
        const slideImage = document.createElement('img');
        slideImage.src = imageSrc; // Use image source from the selectedImages array
        slideImage.alt = `Slide ${index + 1}`;
        slide.appendChild(slideImage);

        // Append slide to the slideshow container
        slideshowContainer.appendChild(slide);
    });

    // Append slideshow container to the document
    const previewSection = document.querySelector('.video-preview');
    previewSection.innerHTML = ''; // Clear existing content
    previewSection.appendChild(slideshowContainer);

    // Create and play background music
    if (selectedMusic) {
        const audioElement = document.createElement('audio');
        audioElement.src = URL.createObjectURL(selectedMusic);
        audioElement.controls = true; // Show controls for audio
        previewSection.appendChild(audioElement);
        audioElement.play();
    }

    // Start the slideshow
    showSlides(1, slideshowContainer, imageDuration);
}


function showSlides(n, slideshowContainer, imageDuration) {
    const slides = slideshowContainer.querySelectorAll('.mySlides');

    // Reset index if out of bounds
    if (n > slides.length) {
        n = 1;
    }
    if (n < 1) {
        n = slides.length;
    }

    // Hide all slides
    slides.forEach((slide) => {
        slide.style.display = 'none';
    });

    // Display the current slide
    slides[n - 1].style.display = 'block';

    // Move to the next slide after a specified duration
    setTimeout(() => {
        showSlides(n + 1, slideshowContainer, imageDuration);
    }, imageDuration * 1000);
}
