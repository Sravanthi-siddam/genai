document.addEventListener('DOMContentLoaded', () => {
    const uploadSection = document.getElementById('uploadSection');
    const imageInput = document.getElementById('imageInput');
    const imagePreview = document.getElementById('imagePreview');
    const previewContainer = document.getElementById('previewContainer');
    const predictBtn = document.getElementById('predictBtn');
    const loader = document.getElementById('loader');
    const resultSection = document.getElementById('resultSection');
    const historyList = document.getElementById('historyList');

    // Load history on startup
    loadHistory();

    // Drag and Drop
    uploadSection.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadSection.classList.add('dragover');
    });

    uploadSection.addEventListener('dragleave', () => {
        uploadSection.classList.remove('dragover');
    });

    uploadSection.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadSection.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });

    // Click to upload
    uploadSection.addEventListener('click', () => {
        imageInput.click();
    });

    imageInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    let currentFile = null;

    function handleFile(file) {
        if (!file.type.startsWith('image/')) {
            alert('Please upload an image file.');
            return;
        }
        currentFile = file;
        const reader = new FileReader();
        reader.onload = (e) => {
            imagePreview.src = e.target.result;
            previewContainer.style.display = 'flex';
            resultSection.style.display = 'none'; // Hide previous results
            predictBtn.disabled = false; // Enable predict button
        };
        reader.readAsDataURL(file);
    }

    // Prediction
    predictBtn.addEventListener('click', async () => {
        if (!currentFile) {
            alert('Please select an image first.');
            return;
        }

        // Show loading
        loader.style.display = 'block';
        predictBtn.disabled = true;
        resultSection.style.display = 'none';

        const formData = new FormData();
        formData.append('file', currentFile);

        try {
            const response = await fetch('http://localhost:5000/predict', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();
            displayResults(data);
            saveToHistory(data);

        } catch (error) {
            console.error('Error:', error);
            alert('Failed to get prediction. Please try again.');
        } finally {
            loader.style.display = 'none';
            predictBtn.disabled = false;
        }
    });

    function displayResults(data) {
        document.getElementById('diseaseName').innerText = data.disease;
        document.getElementById('confidenceScore').innerText = data.confidence;
        document.getElementById('description').innerText = data.description;
        document.getElementById('treatment').innerText = data.treatment;
        document.getElementById('prevention').innerText = data.prevention;

        resultSection.style.display = 'block';
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }

    // LocalStorage History
    function saveToHistory(data) {
        const history = JSON.parse(localStorage.getItem('agroHistory')) || [];
        const newEntry = {
            disease: data.disease,
            confidence: data.confidence,
            date: new Date().toLocaleDateString() + ' ' + new Date().toLocaleTimeString()
        };
        history.unshift(newEntry); // Add to beginning
        if (history.length > 10) history.pop(); // Keep last 10
        localStorage.setItem('agroHistory', JSON.stringify(history));
        loadHistory();
    }

    function loadHistory() {
        const history = JSON.parse(localStorage.getItem('agroHistory')) || [];
        historyList.innerHTML = '';

        if (history.length === 0) {
            historyList.innerHTML = '<li style="text-align:center; color:#666;">No history yet.</li>';
            return;
        }

        history.forEach((item, index) => {
            const li = document.createElement('li');
            li.className = 'history-item';
            li.innerHTML = `
                <div>
                    <strong>${item.disease}</strong> <span class="confidence">${item.confidence}</span>
                    <div class="history-date">${item.date}</div>
                </div>
                <button class="delete-btn" onclick="deleteHistoryItem(${index})">&times;</button>
            `;
            historyList.appendChild(li);
        });
    }

    window.deleteHistoryItem = function (index) {
        const history = JSON.parse(localStorage.getItem('agroHistory')) || [];
        history.splice(index, 1);
        localStorage.setItem('agroHistory', JSON.stringify(history));
        loadHistory();
    };
});
