import { createContext, useContext, useEffect, useRef, useState } from "react";

const ToastContext = createContext(null);

export function ToastProvider({ children }) {
  const [toasts, setToasts] = useState([]);
  const counterRef = useRef(0);

  function addToast(message, tone = "success") {
    const id = counterRef.current++;
    setToasts((current) => [...current, { id, message, tone }]);
    return id;
  }

  function removeToast(id) {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }

  useEffect(() => {
    if (!toasts.length) {
      return undefined;
    }

    const timers = toasts.map((toast) =>
      window.setTimeout(() => {
        removeToast(toast.id);
      }, 3200)
    );

    return () => timers.forEach((timer) => window.clearTimeout(timer));
  }, [toasts]);

  return (
    <ToastContext.Provider value={{ addToast }}>
      {children}
      <div className="toast-stack" aria-live="polite" aria-atomic="true">
        {toasts.map((toast) => (
          <div key={toast.id} className={`toast toast-${toast.tone}`}>
            <div className="toast-mark">{toast.tone === "success" ? "OK" : "!"}</div>
            <div className="toast-copy">
              <strong>{toast.tone === "success" ? "Success" : "Notice"}</strong>
              <span>{toast.message}</span>
            </div>
            <button className="toast-close" onClick={() => removeToast(toast.id)} type="button">
              x
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within ToastProvider");
  }
  return context;
}
