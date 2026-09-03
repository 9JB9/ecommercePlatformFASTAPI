import { Link } from "react-router-dom"
import "../css/NavBar.css"
function NavBar ({username}) {
    return (
        <div className="nav-content">
            <h1>SNEAKRS.</h1>
            <input type="text"></input> {/* might include a div here instead so that I may include a button... but that
                                            will depend on the search mechanism that I use */}
            <Link to = {`/${username}/cart`}>Cart</Link>
        </div>
    )
}

export default NavBar