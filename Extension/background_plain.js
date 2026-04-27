


chrome.action.onClicked.addListener(async (tab) => {
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
        overflow: "hidden"
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

        const closePopupBtn = document.createElement("button");
        closePopupBtn.innerText = "×";
        Object.assign(closePopupBtn.style, {
          cursor: "pointer",
          fontSize: "20px",
          background: "transparent",
          border: "none"
        });
        closePopupBtn.onclick = () => popup.remove();
        popupHeader.appendChild(closePopupBtn);
        contentBox.appendChild(popupHeader);

        const contentArea = document.createElement("div");
        contentArea.innerText = answer || "No answer available.";
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
