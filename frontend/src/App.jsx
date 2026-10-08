import { NavLink, Route, Routes } from "react-router-dom";
import Overview from "./pages/Overview.jsx";
import Feedback from "./pages/Feedback.jsx";
import Teacher from "./pages/Teacher.jsx";
import Analyzer from "./pages/Analyzer.jsx";
import Model from "./pages/Model.jsx";

export default function App() {
  return (
    <>
      <header className="topbar">
        <div className="topbar-inner">
          <NavLink to="/" className="brand">Feedback Desk</NavLink>
          <nav aria-label="Main">
            <NavLink to="/" end>Overview</NavLink>
            <NavLink to="/feedback">Give feedback</NavLink>
            <NavLink to="/analyze">Analyze a comment</NavLink>
            <NavLink to="/model">Model</NavLink>
          </nav>
        </div>
      </header>
      <main className="page">
        <Routes>
          <Route path="/" element={<Overview />} />
          <Route path="/feedback" element={<Feedback />} />
          <Route path="/teachers/:name" element={<Teacher />} />
          <Route path="/analyze" element={<Analyzer />} />
          <Route path="/model" element={<Model />} />
          <Route path="*" element={<p className="note">Page not found.</p>} />
        </Routes>
      </main>
      <footer className="foot">
        AI subject project. Sentiment is predicted from comment text with TF-IDF and Logistic Regression.
      </footer>
    </>
  );
}
