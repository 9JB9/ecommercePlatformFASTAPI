import "../css/ItemCard.css"
import { Link } from "react-router-dom"

function ItemCard({sneaker}) {
    const sneaker_name = sneaker.name
    const sneaker_price = sneaker.price
    const sneaker_url = sneaker.link
    const sneaker_img_url = sneaker.image_url
    
    return (
        <div className="item-card">
            <Link to = {sneaker_url}>
                <img src={sneaker_img_url}></img>
                <div className="item-card-info"> 
                    <h2>${sneaker_price}</h2>
                    {/* <h3>{sneaker_name}</h3> */}
                    <p>{sneaker_name}</p>
                </div>
            </Link>
        </div>        
    )
}

export default ItemCard