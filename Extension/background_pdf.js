


chrome.action.onClicked.addListener(async (tab) => {
  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ["libs/marked.min.js","libs/html2pdf.bundle.min.js"]
  });
  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: async () => {
      const text = window.getSelection().toString();
      let apiData = null;

      // Remove existing viewer if any
      const existing = document.getElementById("highlight-viewer");
      if (existing) existing.remove();

      // Floating selection viewer
      const div = document.createElement("div");
      div.id = "highlight-viewer";
      Object.assign(div.style, {
        position: "fixed",
        top: "20px",
        right: "20px",
        width: "350px",
        maxHeight: "350px",
        background: "#f9fafb",
        border: "1px solid #ddd",
        borderRadius: "12px",
        boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
        zIndex: "999999",
        fontFamily: "Segoe UI, sans-serif",
        color: "#333",
        display: "flex",
        flexDirection: "column",
        overflow: "hidden",
        textAlign: "justify",
      });

      // Header
      const header = document.createElement("div");
      Object.assign(header.style, {
        background: "#007BFF",
        color: "white",
        padding: "8px 12px",
        fontSize: "16px",
        fontWeight: "bold",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center"
      });
      header.innerText = "VLANC Indian Legal Agents";

      const closeBtn = document.createElement("button");
      closeBtn.innerText = "×";
      Object.assign(closeBtn.style, {
        background: "transparent",
        color: "white",
        border: "none",
        fontSize: "20px",
        cursor: "pointer",
        marginLeft: "10px"
      });
      closeBtn.onclick = () => div.remove();
      header.appendChild(closeBtn);
      div.appendChild(header);

      // Scrollable text area
      const textDiv = document.createElement("div");
      textDiv.innerText = text || "Which section of Indian Act do you want to see?";
      Object.assign(textDiv.style, {
        flex: "1",
        overflowY: "auto",
        padding: "12px",
        fontSize: "14px",
        lineHeight: "1.4",
        background: "white"
      });
      div.appendChild(textDiv);

      // Spinner
      const spinner = document.createElement("div");
      spinner.innerHTML = `
        <div style="
          border: 4px solid #f3f3f3;
          border-top: 4px solid #007BFF;
          border-radius: 50%;
          width: 30px;
          height: 30px;
          animation: spin 1s linear infinite;
          margin: auto;
        "></div>
        <style>
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        </style>
      `;
      Object.assign(spinner.style, {
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        padding: "10px",
        background: "#f1f3f5"
      });
      div.appendChild(spinner);

      // Button container
      const buttonContainer = document.createElement("div");
      Object.assign(buttonContainer.style, {
        display: "none", // Hide until data arrives
        gridTemplateColumns: "repeat(2, 1fr)",
        gap: "10px",
        padding: "12px",
        background: "#f1f3f5"
      });

      const buttonToKey = {
        "IT ACT": "IT_Act_Agent_answer",
        "BNS": "BNS_Act_Agent_answer",
        "BSA": "BSA_Act_Agent_answer",
        "Web Search": "Web_Search_answer"
      };

      ["IT ACT", "BNS", "BSA", "Web Search"].forEach(name => {
        const btn = document.createElement("button");
        btn.innerText = name;
        Object.assign(btn.style, {
          padding: "8px",
          background: "#007BFF",
          color: "white",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer",
          fontSize: "14px",
          transition: "background 0.2s"
        });
        btn.onmouseover = () => (btn.style.background = "#0056b3");
        btn.onmouseout = () => (btn.style.background = "#007BFF");

        btn.onclick = () => {
          const answer = apiData ? apiData[buttonToKey[name]] : "No data available.";
          showPopup(name, answer);
        };

        buttonContainer.appendChild(btn);
      });

      div.appendChild(buttonContainer);
      document.body.appendChild(div);

      // Fetch data from API immediately
      try {
        const response = await fetch("http://127.0.0.1:8000/chatbot/api/chat/", {
          method: "POST",
          headers: { "Content-Type": "application/json", "Accept": "*/*" },
          body: JSON.stringify({ user_input: text })
        });
        apiData = await response.json();
        spinner.style.display = "none"; // Hide spinner
        buttonContainer.style.display = "grid"; // Show buttons
      } catch (error) {
        spinner.innerText = "Error loading data.";
      }

      function showPopup(name, answer) {
        const popup = document.createElement("div");
        popup.id = "full-popup";
        Object.assign(popup.style, {
          position: "fixed",
          top: "0",
          left: "0",
          width: "100%",
          height: "100%",
          background: "rgba(0,0,0,0.5)",
          zIndex: "1000000",
          display: "flex",
          alignItems: "center",
          justifyContent: "center"
        });

        const contentBox = document.createElement("div");
        Object.assign(contentBox.style, {
          background: "white",
          width: "80%",
          maxHeight: "80%",
          borderRadius: "8px",
          padding: "20px",
          overflowY: "auto",
          position: "relative",
          boxShadow: "0 4px 12px rgba(0,0,0,0.3)",
          display: "flex",
          flexDirection: "column"
        });

        const popupHeader = document.createElement("div");
        Object.assign(popupHeader.style, {
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "10px",
          fontWeight: "bold",
          fontSize: "18px"
        });
        popupHeader.innerText = `${name} Details`;
        const Download_pdf = document.createElement("button");
        // function downloadMarkdown() {
        //   const markdownText = answer;
        //   const blob = new Blob([markdownText], { type: "text/markdown" });
        //   const url = URL.createObjectURL(blob);
        //   const link = document.createElement("a");
        //   link.href = url;
        //   link.download = "markdown.md";
        //   document.body.appendChild(link);
        //   link.click();
        //   document.body.removeChild(link);
        //   URL.revokeObjectURL(url);
        // }

        function downloadMarkdown() {
      const element = document.getElementById("content-box");
      const now = new Date();

          // Format date: 21_Jul_2025_08_45PM
          const options = { day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit', hour12: true };
          const formatter = new Intl.DateTimeFormat('en-US', options);
          const parts = formatter.formatToParts(now);
          const day = parts.find(p => p.type === 'day').value;
          const month = parts.find(p => p.type === 'month').value;
          const year = parts.find(p => p.type === 'year').value;
          const hour = parts.find(p => p.type === 'hour').value.padStart(2, '0');
          const minute = parts.find(p => p.type === 'minute').value;
          const dayPeriod = parts.find(p => p.type === 'dayPeriod').value;

          const timestamp = `${day}_${month}_${year}_${hour}_${minute}_${dayPeriod}`; 
      html2pdf().set({
        margin: 10,
        filename: `${name.replaceAll(" ", "_")}-${timestamp}.pdf`,
        html2canvas: { scale: 2 },
        jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
      }).from(element).save();
    }


        Download_pdf.onclick = downloadMarkdown;
        Download_pdf.innerText = "📥";  
        Object.assign(Download_pdf.style, {
          fontSize: "24px",
          background: "transparent",
          border: "none",
          cursor: "pointer",
          padding: "4px",
          marginRight: "4px"  
        });
        const container = document.createElement("div");
        const closePopupBtn = document.createElement("button");
        closePopupBtn.innerText = "×";
        Object.assign(closePopupBtn.style, {
          cursor: "pointer",
          fontSize: "30px",
          background: "transparent",
          border: "none",
          color:"black"
        });
        closePopupBtn.onclick = () => popup.remove();
        container.appendChild(Download_pdf);
        container.appendChild(closePopupBtn);
        popupHeader.appendChild(container)
        contentBox.appendChild(popupHeader);


        const contentArea = document.createElement("div");
        const html = marked(answer || "**No answer available**.", { breaks: true });
        contentArea.id = "content-box";
        contentArea.innerHTML = html;
        // contentArea.innerText = answer || "No answer available.";
        Object.assign(contentArea.style, {
          overflowY: "auto",
          flex: "1",
          paddingTop: "10px"
        });
        contentBox.appendChild(contentArea);

        popup.appendChild(contentBox);
        document.body.appendChild(popup);
      }
    }
  });
});
