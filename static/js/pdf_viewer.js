// PDF Viewer JavaScript for Resume Analyzer application

// Initialize PDF viewer when the document is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializePdfViewer();
});

// Initialize PDF viewer using PDF.js
function initializePdfViewer() {
    const pdfContainer = document.getElementById('pdf-container');
    if (!pdfContainer) return;
    
    const pdfUrl = pdfContainer.dataset.pdfUrl;
    if (!pdfUrl) return;
    
    // Load the PDF document
    const loadingTask = pdfjsLib.getDocument(pdfUrl);
    loadingTask.promise.then(function(pdf) {
        // Get the first page
        pdf.getPage(1).then(function(page) {
            const scale = 1.5;
            const viewport = page.getViewport({ scale: scale });
            
            // Prepare canvas for rendering
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.height = viewport.height;
            canvas.width = viewport.width;
            canvas.classList.add('w-100', 'h-auto');
            
            // Add canvas to container
            pdfContainer.appendChild(canvas);
            
            // Render PDF page on the canvas
            const renderContext = {
                canvasContext: context,
                viewport: viewport
            };
            
            page.render(renderContext);
        });
    }, function(error) {
        // Display error
        pdfContainer.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle-fill me-2"></i>
                Failed to load PDF: ${error.message}
            </div>
        `;
    });
}

// Function to extract text from the PDF file
function extractTextFromPdf(pdfUrl, callback) {
    pdfjsLib.getDocument(pdfUrl).promise.then(function(pdf) {
        let allText = '';
        
        // Function to extract text from a single page
        function getPageText(pageNum) {
            return pdf.getPage(pageNum).then(function(page) {
                return page.getTextContent().then(function(textContent) {
                    return textContent.items.map(item => item.str).join(' ');
                });
            });
        }
        
        // Extract text from all pages
        const pagePromises = [];
        for (let i = 1; i <= pdf.numPages; i++) {
            pagePromises.push(getPageText(i));
        }
        
        Promise.all(pagePromises).then(function(pageTexts) {
            allText = pageTexts.join('\n');
            callback(allText);
        });
    }).catch(function(error) {
        console.error('Error extracting text from PDF:', error);
        callback('');
    });
}
