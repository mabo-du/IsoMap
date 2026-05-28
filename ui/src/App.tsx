import { ImportWizard } from "./components/ImportWizard/ImportWizard";
import "./App.css";

function App() {
  return (
    <main className="container">
      <h1>IsoMap</h1>
      <p>Isotopic and paleoecological data standardisation middleware</p>
      
      <ImportWizard />
    </main>
  );
}

export default App;
