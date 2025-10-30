document.addEventListener('DOMContentLoaded', function() {
    const postersGrid = document.getElementById('posters-grid');
    const tagFilter = document.getElementById('tag-filter');
    let allPosters = [];
    let allTags = new Set();

    // Fetch data from the JSON file
    fetch('posters.json')
        .then(response => response.json())
        .then(data => {
            allPosters = data;
            populateTags();
            displayPosters(allPosters);
        });

    function populateTags() {
        allPosters.forEach(poster => {
            poster.tags.forEach(tag => allTags.add(tag));
        });

        allTags.forEach(tag => {
            const option = document.createElement('option');
            option.value = tag;
            option.textContent = tag;
            tagFilter.appendChild(option);
        });
    }

    function displayPosters(posters) {
        postersGrid.innerHTML = '';
        posters.forEach(poster => {
            const posterCard = document.createElement('div');
            posterCard.className = 'poster-card';

            // Create and append the image
            const img = document.createElement('img');
            img.src = '../' + poster.image_path; // Adjust path to be relative to the frontend directory
            posterCard.appendChild(img);

            // Create and append the tags container
            const tagsContainer = document.createElement('div');
            tagsContainer.className = 'tags';
            poster.tags.forEach(tag => {
                const tagSpan = document.createElement('span');
                tagSpan.textContent = tag;
                tagsContainer.appendChild(tagSpan);
            });
            posterCard.appendChild(tagsContainer);

            postersGrid.appendChild(posterCard);
        });
    }

    tagFilter.addEventListener('change', function() {
        const selectedTag = this.value;
        if (selectedTag === '') {
            displayPosters(allPosters);
        } else {
            const filteredPosters = allPosters.filter(poster => poster.tags.includes(selectedTag));
            displayPosters(filteredPosters);
        }
    });
});
