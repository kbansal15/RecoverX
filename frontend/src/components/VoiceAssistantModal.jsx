import React, { useState } from "react";
import { X, Mic, Send, Volume2, Sparkles, Calendar, CheckCircle2, ShieldAlert } from "lucide-react";

export function VoiceAssistantModal({ caseData, onClose, onVoiceTurn }) {
  const [transcript, setTranscript] = useState("");
  const [loading, setLoading] = useState(false);
  const [conversation, setConversation] = useState([
    {
      sender: "agent",
      text: `Namaste ${caseData?.customer?.name?.split(" ")[0] || "Sir"}, main Razorpay merchant support se baat kar raha hoon. Aapka ₹${caseData?.amount?.toLocaleString('en-IN')} ka order payment incomplete reh gaya tha. Kya main aapki help kar sakta hoon?`
    }
  ]);
  const [lastResult, setLastResult] = useState(null);

  if (!caseData) return null;

  const quickPhrases = [
    { label: "Pay Now (अभी पे करेंगे)", text: "Haan, abhi payment kar deta hoon, link bhej do." },
    { label: "Pay Later (3 दिन बाद)", text: "Main 3 din baad salary aane par pakka payment karunga." },
    { label: "Method Failed (कार्ड रिजेक्ट)", text: "Mera card reject ho gaya tha, koi dusra payment option hai kya?" },
    { label: "Cancel Order (कैंसल करो)", text: "Nahi chahiye mujhe, cancel kardo and dubara call mat karna." },
    { label: "Escalate to Human (मैनेजर)", text: "Mujhe support manager se baat karvao." }
  ];

  const handleSend = async (textToSend) => {
    const text = textToSend || transcript;
    if (!text.trim()) return;

    const userMsg = { sender: "user", text };
    setConversation((prev) => [...prev, userMsg]);
    setTranscript("");
    setLoading(true);

    try {
      const res = await onVoiceTurn(caseData.id, text);
      setLastResult(res);

      const agentMsg = { sender: "agent", text: res.spoken_response };
      setConversation((prev) => [...prev, agentMsg]);

      // Speak back using browser Web Speech API
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utter = new SpeechSynthesisUtterance(res.spoken_response);
        utter.lang = "hi-IN";
        utter.rate = 1.0;
        window.speechSynthesis.speak(utter);
      }
    } catch (err) {
      setConversation((prev) => [
        ...prev,
        { sender: "agent", text: "Maaf kijiye, network issue ki wajah se samajh nahi paaye. Kripya dobara try karein." }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="checkout-modal-backdrop" onClick={onClose}>
      <div className="checkout-box" style={{ width: 500 }} onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="checkout-top" style={{ background: 'linear-gradient(135deg, #0b1426 0%, #0c2340 100%)' }}>
          <div>
            <div style={{ fontSize: '11px', textTransform: 'uppercase', color: '#38bdf8', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 5 }}>
              <Sparkles size={12} /> Hinglish Voice Recovery Agent
            </div>
            <div style={{ fontSize: '16px', fontWeight: 800 }}>
              Live Call: {caseData.customer?.name}
            </div>
            <div style={{ fontSize: '12px', color: '#94a3b8' }}>
              Amount: ₹{caseData.amount?.toLocaleString('en-IN')} • Case #{caseData.id?.slice(0, 8)}
            </div>
          </div>
          <button onClick={onClose} style={{ background: 'none', border: 'none', color: '#ffffff', cursor: 'pointer' }}>
            <X size={18} />
          </button>
        </div>

        {/* Animated Waveform */}
        <div style={{ backgroundColor: '#f8fafc', padding: '12px 20px', borderBottom: '1px solid var(--rzp-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <Volume2 size={16} color="#0c8ce9" />
            <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--rzp-navy)' }}>
              {loading ? "Classifying Speech with Gemini NLU..." : "Voice Channel Active (Hinglish/English)"}
            </span>
          </div>
          <div className="waveform-container" style={{ margin: 0, height: 24 }}>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
            <div className="wave-bar"></div>
          </div>
        </div>

        {/* Conversation Area */}
        <div style={{ padding: '16px', height: 240, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 10, backgroundColor: '#ffffff' }}>
          {conversation.map((msg, i) => (
            <div
              key={i}
              style={{
                alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '85%',
                padding: '10px 14px',
                borderRadius: '12px',
                fontSize: '13px',
                lineHeight: 1.4,
                backgroundColor: msg.sender === 'user' ? 'var(--rzp-blue)' : '#f1f5f9',
                color: msg.sender === 'user' ? '#ffffff' : 'var(--rzp-navy)',
                boxShadow: 'var(--shadow-sm)'
              }}
            >
              {msg.text}
            </div>
          ))}
        </div>

        {/* NLU & Action Badge Display */}
        {lastResult && (
          <div style={{ padding: '8px 16px', backgroundColor: '#f0fdf4', borderTop: '1px solid #bbf7d0', fontSize: '12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: '#166534', fontWeight: 600 }}>
              <CheckCircle2 size={14} /> Intent: {lastResult.intent} ({lastResult.classifier})
            </div>
            {lastResult.promise_to_pay && (
              <span style={{ color: '#0369a1', fontWeight: 600 }}>
                📅 PTP Scheduled
              </span>
            )}
            {lastResult.payment_link_url && (
              <span style={{ color: '#059669', fontWeight: 600 }}>
                🔗 Payment Link Created
              </span>
            )}
          </div>
        )}

        {/* Quick Phrases */}
        <div style={{ padding: '12px 16px', backgroundColor: '#f8fafc', borderTop: '1px solid var(--rzp-border)' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', color: 'var(--rzp-text-muted)', marginBottom: 8 }}>
            Simulate Customer Speaking
          </div>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
            {quickPhrases.map((qp, i) => (
              <button
                key={i}
                disabled={loading}
                onClick={() => handleSend(qp.text)}
                style={{
                  fontSize: '11.5px',
                  padding: '4px 8px',
                  borderRadius: '6px',
                  border: '1px solid var(--rzp-border)',
                  backgroundColor: '#ffffff',
                  color: 'var(--rzp-navy)',
                  cursor: 'pointer',
                  fontWeight: 500
                }}
              >
                {qp.label}
              </button>
            ))}
          </div>
        </div>

        {/* Input Bar */}
        <div style={{ padding: '12px 16px', display: 'flex', gap: 8, borderTop: '1px solid var(--rzp-border)', backgroundColor: '#ffffff' }}>
          <input
            type="text"
            placeholder="Type or speak in Hinglish (e.g. 'Abhi pay kar deta hoon')..."
            value={transcript}
            onChange={(e) => setTranscript(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            style={{
              flex: 1,
              padding: '8px 12px',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--rzp-border)',
              fontSize: '13px',
              outline: 'none'
            }}
          />
          <button
            onClick={() => handleSend()}
            disabled={loading}
            className="btn btn-primary btn-sm"
          >
            <Send size={14} />
          </button>
        </div>
      </div>
    </div>
  );
}
