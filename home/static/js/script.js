document.addEventListener("DOMContentLoaded", () => {
    const highlightButton = document.getElementById("highlight-button");
    const messageInput = document.getElementById("message-input");
    const content = document.getElementById("content");
    const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    
    // Initialization Functions
    function initializeTippyTooltips() {
        document.querySelectorAll(".highlight-word").forEach((element) => {
            if (element._tippy) {
                element._tippy.destroy();
            }

            const trigger = window.innerWidth <= 768 ? "click" : "mouseenter";

            tippy(element, {
                content: "loading...",
                allowHTML: true,
                interactive: true,
                delay: [300, 100],
                theme: "custom-tooltip",
                trigger: trigger,
                placement: "auto",
                onShow(instance) {
                    const term = instance.reference.getAttribute("data-term");
                    if (!term || instance.state.loading) return;

                    instance.state.loading = true;

                    fetch(`/fetch-summary?term=${encodeURIComponent(term)}`, {
                        headers: {
                            "X-CSRFToken": csrftoken,
                        },
                    })
                        .then((response) => {
                            if (!response.ok) {
                                throw new Error(`HTTP error! status: ${response.status}`);
                            }
                            return response.json();
                        })
                        .then((data) => {
                            const tooltipContent = data.summary
                                ? `
                                    <div class="tooltip-content">
                                        <h4 class="tooltip-title">${term}</h4>
                                        <p class="tooltip-summary">${data.summary}...</p>
                                        <a href="${data.link}" target="_blank" class="tooltip-link">More Info</a>
                                    </div>
                                `
                                : "No information available.";

                            instance.setContent(tooltipContent);
                        })
                        .catch((error) => {
                            console.error("Error fetching summary:", error);
                            instance.setContent("Error fetching info");
                            instance.state.loading = false;
                        });
                },
            });
        });
    }

    function initializeTooltipStyles() {
        const tooltipStyle = document.createElement("style");
        tooltipStyle.textContent = `
            .tippy-box[data-theme~='custom-tooltip'] {
                background-color: #2c3e50 !important;
                color: #ecf0f1 !important;
                border-radius: 8px !important;
                padding: 0.75rem !important;
                font-size: 0.875rem !important;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
            }

            .tooltip-content {
                max-width: 250px;
            }

            .tooltip-title {
                color: #3498db;
                margin-bottom: 0.5rem;
                font-weight: 600;
            }

            .tooltip-summary {
                margin-bottom: 0.5rem;
                line-height: 1.4;
            }

            .tooltip-link {
                color: #3498db;
                text-decoration: none;
                font-weight: 600;
                display: inline-block;
                margin-top: 0.5rem;
            }
        `;
        document.head.appendChild(tooltipStyle);
    }

    
    // Helper Functions
    function resetHighlightButton() {
        highlightButton.disabled = false;
        highlightButton.textContent = "Highlight";
    }

    function getErrorMessage(error) {
        const errorBox = document.createElement("div");
        errorBox.style.backgroundColor = "rgba(249, 58, 55, .10)";
        errorBox.style.border = "1px solid rgba(249, 58, 55, .16)";
        errorBox.style.borderRadius = "8px";
        errorBox.style.padding = "18px";
        errorBox.style.margin = "16px 0";
        errorBox.style.color = "darkred";
        errorBox.style.display = "inline-block";
        errorBox.style.width = "-webkit-fill-available";
        errorBox.style.textAlign = "center";

        errorBox.textContent = error;
        content.innerHTML = "";
        content.appendChild(errorBox);
    }


    // Event Handlers
    async function sendMessage() {
        const message = messageInput.value;

        if (!message) {
            messageInput.value = "";
            return;
        }

        highlightButton.disabled = true;
        highlightButton.textContent = "Finding Highlights...";

        if (!navigator.onLine) {
            getErrorMessage(
                "It seems you're offline right now. Please check your internet connection and try again."
            );
            resetHighlightButton();
            return;
        }

        messageInput.value = "";
        messageInput.style.height = "auto";

        try {
            const response = await fetch("/send_message", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrftoken,
                },
                body: JSON.stringify({ message }),
            });

            if (!response.ok) {
                throw new Error(`Server error: ${response.status}`);
            }

            const data = await response.json();
            content.innerHTML = data.highlight;
            resetHighlightButton();
            initializeTippyTooltips();
        } catch (error) {
            getErrorMessage("Failed to fetch highlights. Please try again.");
            resetHighlightButton();
        }
    }

    function adjustTextareaHeight() {
        const minHeight = 30;
        const lineHeight = 20;
        const maxHeight = 170;
        messageInput.style.height = "auto";
        const lines = Math.max(Math.floor(messageInput.scrollHeight / lineHeight), 1);
        const newHeight = minHeight + (lines - 1) * lineHeight;
        messageInput.style.height = Math.min(Math.max(newHeight, minHeight), maxHeight) + "px";
    }


    // Event Listeners
    messageInput.addEventListener("input", adjustTextareaHeight);

    highlightButton.addEventListener("click", () => {
        sendMessage()
    });

    messageInput.addEventListener("keypress", (e) => {
        if (e.key === "Enter" && !highlightButton.disabled) {
            sendMessage();
        }
    });


    // Initialization
    initializeTooltipStyles();
    initializeTippyTooltips();
});
