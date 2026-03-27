import logo_img from './assets/Signal analysis.gif'

function PageNotFound(){

    return (
        <>
        <img src={logo_img} height={'300px'} width={'300px'} alt='Page Not Found'/>
        <h1>404 - Page Not Found</h1>
        <p>Oops! The page you're looking for doesn't exist or has been moved.</p>

        <a href="/">Go to Home</a>
        </>
    )
}

export default PageNotFound;