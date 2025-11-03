import { NavLink } from "react-router-dom";
import { Home, Plus, List, Zap } from "lucide-react";

const Navbar = () => {
  return (
    <nav className="brutal-border border-b-8 bg-card p-2 sm:p-4">
      <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 sm:gap-0">
        {/* Logo */}
        <div className="flex items-center gap-2 min-w-0 flex-1 sm:flex-initial">
          <div className="brutal-border brutal-shadow-sm bg-primary p-1.5 sm:p-2 flex-shrink-0">
            <Zap className="w-5 h-5 sm:w-8 sm:h-8 text-primary-foreground" />
          </div>
          <div className="font-bold text-base sm:text-xl md:text-2xl whitespace-nowrap">
            <span className="text-foreground">POST</span>
            <span className="text-accent">BLASTER</span>
          </div>
          <div className="text-xs sm:text-sm font-bold text-muted-foreground hidden md:block">
            AI SOCIAL MEDIA GENERATOR
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-2 w-full sm:w-auto justify-end sm:justify-start">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `brutal-border brutal-shadow-sm px-3 sm:px-4 md:px-6 py-2 sm:py-2.5 md:py-3 font-bold uppercase transition-all hover:translate-x-1 hover:translate-y-1 hover:shadow-none text-xs sm:text-sm md:text-base min-h-[44px] flex items-center justify-center ${
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "bg-card text-foreground hover:bg-muted"
              }`
            }
          >
            <Home className="w-4 h-4 sm:w-5 sm:h-5" />
            <span className="hidden sm:inline ml-1 sm:ml-2">CREATE</span>
          </NavLink>

          <NavLink
            to="/posts"
            className={({ isActive }) =>
              `brutal-border brutal-shadow-sm px-3 sm:px-4 md:px-6 py-2 sm:py-2.5 md:py-3 font-bold uppercase transition-all hover:translate-x-1 hover:translate-y-1 hover:shadow-none text-xs sm:text-sm md:text-base min-h-[44px] flex items-center justify-center ${
                isActive
                  ? "bg-accent text-accent-foreground"
                  : "bg-card text-foreground hover:bg-muted"
              }`
            }
          >
            <List className="w-4 h-4 sm:w-5 sm:h-5" />
            <span className="hidden sm:inline ml-1 sm:ml-2">POSTS</span>
          </NavLink>

          <NavLink
            to="/connect"
            className={({ isActive }) =>
              `brutal-border brutal-shadow-sm px-3 sm:px-4 md:px-6 py-2 sm:py-2.5 md:py-3 font-bold uppercase transition-all hover:translate-x-1 hover:translate-y-1 hover:shadow-none text-xs sm:text-sm md:text-base min-h-[44px] flex items-center justify-center ${
                isActive
                  ? "bg-secondary text-secondary-foreground"
                  : "bg-card text-foreground hover:bg-muted"
              }`
            }
          >
            <Zap className="w-4 h-4 sm:w-5 sm:h-5" />
            <span className="hidden sm:inline ml-1 sm:ml-2">CONNECT</span>
          </NavLink>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;