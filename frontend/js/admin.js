const API_URL = 'http://localhost:8002';

async function uploadAssessment() {
    const category = document.getElementById('assessmentCategory').value.trim();
    const file = document.getElementById('assessmentFile').files[0];
    const text = document.getElementById('assessmentText').value.trim();
    const statusDiv = document.getElementById('assessmentStatus');
    
    if (!category) {
        showStatus(statusDiv, 'Please enter a category name', 'error');
        return;
    }
    
    if (!file && !text) {
        showStatus(statusDiv, 'Please upload a file or enter text', 'error');
        return;
    }
    
    try {
        if (text) {
            // Upload text directly
            await uploadTextData(text, 'assessment', category, statusDiv);
        } else {
            // Upload file
            await uploadFileData(file, 'assessment', category, statusDiv);
        }
        
        // Clear form
        document.getElementById('assessmentCategory').value = '';
        document.getElementById('assessmentFile').value = '';
        document.getElementById('assessmentText').value = '';
        
    } catch (error) {
        console.error('Upload error:', error);
        showStatus(statusDiv, 'Upload failed: ' + error.message, 'error');
    }
}

async function uploadExercise() {
    const category = document.getElementById('exerciseCategory').value.trim();
    const file = document.getElementById('exerciseFile').files[0];
    const text = document.getElementById('exerciseText').value.trim();
    const statusDiv = document.getElementById('exerciseStatus');
    
    if (!category) {
        showStatus(statusDiv, 'Please enter a category name', 'error');
        return;
    }
    
    if (!file && !text) {
        showStatus(statusDiv, 'Please upload a file or enter text', 'error');
        return;
    }
    
    try {
        if (text) {
            // Upload text directly
            await uploadTextData(text, 'exercise', category, statusDiv);
        } else {
            // Upload file
            await uploadFileData(file, 'exercise', category, statusDiv);
        }
        
        // Clear form
        document.getElementById('exerciseCategory').value = '';
        document.getElementById('exerciseFile').value = '';
        document.getElementById('exerciseText').value = '';
        
    } catch (error) {
        console.error('Upload error:', error);
        showStatus(statusDiv, 'Upload failed: ' + error.message, 'error');
    }
}

async function uploadTextData(content, type, category, statusDiv) {
    showStatus(statusDiv, 'Uploading and embedding...', 'info');
    
    const formData = new FormData();
    formData.append('content', content);
    formData.append('data_type', type);
    formData.append('category', category);
    
    const response = await fetch(`${API_URL}/data/upload/text`, {
        method: 'POST',
        body: formData
    });
    
    const data = await response.json();
    
    if (response.ok) {
        showStatus(statusDiv, `✓ ${data.message}`, 'success');
    } else {
        showStatus(statusDiv, `✗ ${data.detail}`, 'error');
    }
}

async function uploadFileData(file, type, category, statusDiv) {
    showStatus(statusDiv, 'Uploading and embedding...', 'info');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('category', category);
    
    const endpoint = type === 'assessment' ? '/data/upload/assessment' : '/data/upload/exercise';
    
    const response = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        body: formData
    });
    
    const data = await response.json();
    
    if (response.ok) {
        showStatus(statusDiv, `✓ ${data.message} (${data.count} documents)`, 'success');
    } else {
        showStatus(statusDiv, `✗ ${data.detail}`, 'error');
    }
}

function showStatus(element, message, type) {
    element.textContent = message;
    element.className = `status-message ${type}`;
    element.style.display = 'block';
    
    if (type === 'success') {
        setTimeout(() => {
            element.style.display = 'none';
        }, 5000);
    }
}