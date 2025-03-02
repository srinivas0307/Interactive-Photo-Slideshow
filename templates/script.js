document.addEventListener('DOMContentLoaded', function () {
    // Add event listener for file input change
    const imageUpload = document.getElementById('imageUpload');
    const uploadButton = document.getElementById('upload-button');
    const dragDropArea = document.getElementById('dragDropArea');
    const selectImagesButton = document.getElementById('select-images-button');
    let selectedImages = [];

    const createSlideshowButton = document.getElementById('createSlideshowButton');
    selectImagesButton.addEventListener('click', selectImagesForSlideshow);
    imageUpload.addEventListener('change', handleImageUpload);
    uploadButton.addEventListener('click', triggerImageUpload);
    dragDropArea.addEventListener('dragover', handleDragOver);
    dragDropArea.addEventListener('dragleave', handleDragLeave);
    dragDropArea.addEventListener('drop', handleDrop);

    // Add event listener for background music change
    const backgroundMusicInput = document.getElementById('backgroundMusic');
    backgroundMusicInput.addEventListener('change', handleBackgroundMusicChange);

    // Add event listener for image duration change
    const imageDurationInput = document.getElementById('imageDuration');
    imageDurationInput.addEventListener('change', handleImageDurationChange);

    // Add event listener for transition effect change
    const transitionEffectSelect = document.getElementById('transitionEffect');
    transitionEffectSelect.addEventListener('change', handleTransitionEffectChange);
});

function handleImageUpload(event) {
    const files = event.target.files;
    displaySelectedImages(files);
}

function triggerImageUpload() {
    // Trigger file input click when label is clicked
    imageUpload.click();
}

function handleDragOver(event) {
    event.preventDefault();
    dragDropArea.classList.add('drag-over');
}

function handleDragLeave(event) {
    event.preventDefault();
    dragDropArea.classList.remove('drag-over');
}

function handleDrop(event) {
    event.preventDefault();
    dragDropArea.classList.remove('drag-over');
    const droppedFiles = event.dataTransfer.files;
    // Convert files object to array
    const filesArray = Array.from(droppedFiles);
    displaySelectedImages(filesArray);
}

function displaySelectedImages(files) {
    const selectedImagesContainer = document.querySelector('.selected-images');
    // Clear previous content
    selectedImagesContainer.innerHTML = '';

    // Display selected images
    for (const file of files) {
        const imageContainer = document.createElement('div');
        imageContainer.classList.add('image-container');
        imageContainer.style.display = 'inline-block'; // Set display to inline-block

        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.value = file.name;
        checkbox.id = file.name;

        const imageElement = document.createElement('img');
        imageElement.src = URL.createObjectURL(file);
        imageElement.alt = file.name;

        imageContainer.appendChild(checkbox);
        imageContainer.appendChild(imageElement);

        selectedImagesContainer.appendChild(imageContainer);
    }
}


function handleBackgroundMusicChange(event) {
    const selectedMusic = event.target.files[0];
    // Handle selected music, e.g., display the filename
    console.log(selectedMusic.name);
}

function handleImageDurationChange(event) {
    const selectedDuration = event.target.value;
    // Handle selected image duration, e.g., update preview
    console.log(selectedDuration);
}

function handleTransitionEffectChange(event) {
    const selectedEffect = event.target.value;
    // Handle selected transition effect, e.g., update preview
    console.log(selectedEffect);
}

function selectImagesForSlideshow() {
    const selectedCheckboxes = document.querySelectorAll('.selected-images input:checked');

    if (selectedCheckboxes.length === 0) {
        alert('No images selected for the slideshow.');
        return;
    }

    // Clear previous selections
    selectedImages = [];

    // Collect selected image sources based on checked checkboxes
    selectedCheckboxes.forEach(checkbox => {
        const imageContainer = checkbox.closest('.image-container');
        const imageElement = imageContainer.querySelector('img');
        selectedImages.push(imageElement.src);
    });

    // Further logic for handling the selected images...
    console.log("Selected Images:", selectedImages);
}


