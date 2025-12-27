import { BrowserRouter, Routes, Route } from "react-router-dom";
import Itinerary from "./pages/Itinerary";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Home / Main page */}
        <Route path="/" element={<Itinerary />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
