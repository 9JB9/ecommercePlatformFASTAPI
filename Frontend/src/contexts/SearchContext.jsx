import { createContext, useEffect, useState, useContext } from "react";

const SearchContext = createContext()
export const useSearchContext = () => useContext(SearchContext)

export const SearchProvider = ({children}) => {
    const [search, setSearch] = useState('')

    // we have to load and save the data now
    useEffect(() => {
        const storedSearch = localStorage.getItem('search')
        if (storedSearch){ // idk if this works with string types, time to find out....
            setSearch(JSON.parse(storedSearch))
        }
    }, [])

    useEffect(() => {
        localStorage.setItem('search', JSON.stringify(search))
    }, [search])

    const updateSearch = (query) => {
        setSearch(query)
    }

    const value = {
        search,
        updateSearch
    }

    return <SearchContext.Provider value={value}>
        {children}
    </SearchContext.Provider>
}