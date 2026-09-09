import { Link } from "react-router-dom"
import { useState } from "react"
import { useSearchContext } from "../contexts/SearchContext"
import "../css/NavBar.css"

function NavBar ({username}) {
    const { search, updateSearch } = useSearchContext()

    return (
        <div className="nav-content">
            <h1><Link to = "/">SNEAKRS.</Link></h1>
            <input name = "searchbar" value={search} type="text"
                onChange={(e) => updateSearch(e.target.value)}></input> {/* might include a div here instead so that I may include a button... but that
                                                                    will depend on the search mechanism that I use */}
            <div className="nav-right">
                <Link to = {`/${username}/cart`}>Cart</Link>
                <Link to = '/login'>Login</Link>
                <Link to = '/Signup'>Signup</Link>
            </div>
        </div>
    )
}

export default NavBar