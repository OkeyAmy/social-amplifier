import { NavLink } from "react-router-dom";
import { Home, Plus, List, Zap } from "lucide-react";

const Navbar = () => {
  return (
    <nav className="brutal-border border-b-8 bg-card p-4">
      <div className="max-w-6xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <div className="flex items-center gap-2">
          <div className="brutal-border brutal-shadow-sm bg-primary p-2">
            <Zap className="w-8 h-8 text-primary-foreground" />
          </div>
          <div className="font-bold text-2xl">
            <span className="text-foreground">POST</span>
            <span className="text-accent">BLASTER</span>
          </div>
          <div className="text-sm font-bold text-muted-foreground">
            AI SOCIAL MEDIA GENERATOR
          </div>
        </div>

        {/* Navigation */}
        <div className="flex items-center gap-2">
          <NavLink
            to="/"
            className={({ isActive }) =>
              `brutal-border brutal-shadow-sm px-6 py-3 font-bold uppercase transition-all hover:translate-x-1 hover:translate-y-1 hover:shadow-none ${
                isActive
                  ? "bg-primary text-primary-foreground"
                  : "bg-card text-foreground hover:bg-muted"
              }`
            }
          >
            <Home className="w-5 h-5 inline mr-2" />
            CREATE
          </NavLink>

          <NavLink
            to="/posts"
            className={({ isActive }) =>
              `brutal-border brutal-shadow-sm px-6 py-3 font-bold uppercase transition-all hover:translate-x-1 hover:translate-y-1 hover:shadow-none ${
                isActive
                  ? "bg-accent text-accent-foreground"
                  : "bg-card text-foreground hover:bg-muted"
              }`
            }
          >
            <List className="w-5 h-5 inline mr-2" />
            POSTS
          </NavLink>

          <NavLink
            to="/connect"
            className={({ isActive }) =>
              `brutal-border brutal-shadow-sm px-6 py-3 font-bold uppercase transition-all hover:translate-x-1 hover:translate-y-1 hover:shadow-none ${
                isActive
                  ? "bg-secondary text-secondary-foreground"
                  : "bg-card text-foreground hover:bg-muted"
              }`
            }
          >
            <Zap className="w-5 h-5 inline mr-2" />
            CONNECT
          </NavLink>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;