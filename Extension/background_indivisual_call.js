chrome.action.onClicked.addListener(async (tab) => {
  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    files: ["libs/marked.min.js", "libs/html2pdf.bundle.min.js"]
  });

  chrome.scripting.executeScript({
    target: { tabId: tab.id },
    func: async () => {
      const text = window.getSelection().toString();

      // Remove existing viewer if any
      const existing = document.getElementById("highlight-viewer");
      if (existing) existing.remove();

      // Add keyframe CSS for spinner
      const styleTag = document.createElement("style");
      styleTag.textContent = `
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `;
      document.head.appendChild(styleTag);

      // Viewer container
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
      header.innerText = "VLANC Indian Legal Agents 🕵️‍♂️";

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

      // Selected Text
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

      // Button container
      const buttonContainer = document.createElement("div");
      Object.assign(buttonContainer.style, {
        display: "grid",
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

      const endpointMap = {
        "IT ACT": "it",
        "BNS": "bns",
        "BSA": "bsa",
        "Web Search": "ws"
      };

      ["IT ACT", "BNS", "BSA", "Web Search"].forEach(name => {
        const btn = document.createElement("button");

        Object.assign(btn.style, {
          padding: "8px",
          background: "#007BFF",
          color: "white",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer",
          fontSize: "14px",
          transition: "background 0.2s",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          gap: "6px"
        });

        const btnText = document.createElement("span");
        btnText.innerText = name;

        const btnSpinner = document.createElement("div");
        btnSpinner.style.display = "none";
        btnSpinner.innerHTML = `
          <div style="
            border: 2px solid #f3f3f3;
            border-top: 2px solid white;
            border-radius: 50%;
            width: 14px;
            height: 14px;
            animation: spin 0.8s linear infinite;
          "></div>
        `;

        btn.onmouseover = () => (btn.style.background = "#0056b3");
        btn.onmouseout = () => (btn.style.background = "#007BFF");

        btn.appendChild(btnText);
        btn.appendChild(btnSpinner);

        btn.onclick = async () => {
          // Show spinner
          btnSpinner.style.display = "inline-block";
          btnText.innerText = "";

          showPopup(name, "Loading...");

          try {
            const response = await fetch(`http://127.0.0.1:8000/VLANC-LegalAI/extension/${endpointMap[name]}`, {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
                "Accept": "*/*"
              },
              body: JSON.stringify({ user_input: text })
            });

            const result = await response.json();
            const key = buttonToKey[name];
            const answer = result[key] || "No data returned.";
            document.getElementById("content-box").innerHTML = marked(answer, { breaks: true });

          } catch (error) {
            document.getElementById("content-box").innerHTML = "⚠️ Failed to fetch data.";
          }

          // Restore button
          btnSpinner.style.display = "none";
          btnText.innerText = name;
        };

        buttonContainer.appendChild(btn);
      });

      div.appendChild(buttonContainer);
      document.body.appendChild(div);

      function showPopup(name, answer) {
        const existingPopup = document.getElementById("full-popup");
        if (existingPopup) existingPopup.remove();

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

        const copyBtn = document.createElement("button");
        copyBtn.innerText = "📋";
        Object.assign(copyBtn.style, {
          fontSize: "20px",
          background: "transparent",
          border: "none",
          cursor: "pointer",
          padding: "4px",
          marginRight: "8px"
        });
        copyBtn.onclick = () => {
          navigator.clipboard.writeText(document.getElementById("content-box")?.innerText || "").then(() => {
            copyBtn.innerText = "☑️";
            setTimeout(() => (copyBtn.innerText = "📋"), 1000);
          });
        };

        const closePopupBtn = document.createElement("button");
        closePopupBtn.innerText = "×";
        Object.assign(closePopupBtn.style, {
          cursor: "pointer",
          fontSize: "28px",
          background: "transparent",
          border: "none",
          color: "black"
        });
        closePopupBtn.onclick = () => {
          popup.remove();
          document.getElementById("minimize-bubble")?.remove();
        };

        const container = document.createElement("div");
        container.appendChild(copyBtn);
        container.appendChild(closePopupBtn);
        popupHeader.appendChild(container);

        const contentArea = document.createElement("div");
        const html = marked(answer || "**No answer available**.", { breaks: true });
        contentArea.id = "content-box";
        contentArea.innerHTML = html;
        Object.assign(contentArea.style, {
          overflowY: "auto",
          flex: "1",
          paddingTop: "10px"
        });

        contentBox.appendChild(popupHeader);
        contentBox.appendChild(contentArea);
        popup.appendChild(contentBox);
        document.body.appendChild(popup);

        const bubble = document.createElement("div");
        bubble.id = "minimize-bubble";
        bubble.innerText = "⚖️";
        Object.assign(bubble.style, {
          position: "fixed",
          bottom: "20px",
          right: "20px",
          width: "48px",
          height: "48px",
          background: "#f9fafb",
          color: "white",
          borderRadius: "50%",
          boxShadow: "0 4px 10px rgba(0,0,0,0.3)",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          fontSize: "22px",
          cursor: "pointer",
          zIndex: "1000001"
        });

        let minimized = false;
        bubble.onclick = () => {
          minimized = !minimized;
          popup.style.display = minimized ? "none" : "flex";
          bubble.innerText = minimized ? "🔍" : "⚖️";
        };

        document.body.appendChild(bubble);
      }
    }
  });
});
