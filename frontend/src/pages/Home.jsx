import "../css/Home.css"
import {useState, useEffect} from "react"
import "../components/NavBar.jsx"
import NavBar from "../components/NavBar.jsx"
import { Link } from "react-router-dom"

function Home() {
    
    const [sneakers, setSneakers] = useState([])
    const username = "" // change this
    // ** write the useEffect to load the shoes here
    // **
    
    return (
        <>
            <div className="home-content">
                <div className="home-nav">
                    <NavBar />
                    <Link to = {`/${username}/cart`}>Cart</Link>
                </div>
                <div className="home-grid">
                    {/* need a loop here to print out the grid of sneaker cards */}
                </div>
            </div>
        </>
    )

}

export default Home