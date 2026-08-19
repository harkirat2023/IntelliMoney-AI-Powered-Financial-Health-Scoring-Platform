const path = require("path");
const fs = require("fs");
const HtmlWebpackPlugin = require("html-webpack-plugin");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");
const webpack = require("webpack");

function loadDotEnv(filePath) {
  const vars = {};
  try {
    const content = fs.readFileSync(filePath, "utf8");
    for (const line of content.split("\n")) {
      const match = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/i);
      if (match) vars[match[1]] = match[2].replace(/^["']|["']$/g, "").trim();
    }
  } catch {
    // .env is optional; real environment variables take precedence below.
  }
  return vars;
}

module.exports = (env, argv) => {
  const isProd = argv.mode === "production";
  const dotenv = loadDotEnv(path.join(__dirname, ".env"));

  const appEnv = {
    API_BASE_URL:
      process.env.API_BASE_URL || dotenv.API_BASE_URL || dotenv.VITE_API_BASE_URL || "/api/v1",
    VITE_WS_HOST: process.env.VITE_WS_HOST || dotenv.VITE_WS_HOST || "",
    VITE_CLERK_PUBLISHABLE_KEY:
      process.env.VITE_CLERK_PUBLISHABLE_KEY ||
      dotenv.VITE_CLERK_PUBLISHABLE_KEY ||
      dotenv.VITE_PUBLIC_CLERK_PUBLISHABLE_KEY ||
      "",
  };

  return {
    mode: isProd ? "production" : "development",
    entry: "./src/main.jsx",
    output: {
      path: path.resolve(__dirname, "dist"),
      filename: "bundle.[contenthash].js",
      chunkFilename: "chunk.[contenthash].js",
      publicPath: "/",
      clean: true,
    },
    resolve: {
      extensions: [".js", ".jsx", ".json"],
      alias: {
        "@": path.resolve(__dirname, "src"),
      },
    },
    module: {
      rules: [
        {
          test: /\.(js|jsx)$/,
          exclude: /node_modules/,
          use: {
            loader: "babel-loader",
            options: {
              presets: [
                ["@babel/preset-env", { targets: "defaults" }],
                ["@babel/preset-react", { runtime: "automatic" }],
              ],
            },
          },
        },
        {
          test: /\.css$/,
          use: ["style-loader", "css-loader", "postcss-loader"],
        },
        {
          test: /\.(png|jpg|jpeg|gif|svg)$/,
          type: "asset/resource",
        },
      ],
    },
    plugins: [
      new CleanWebpackPlugin(),
      new HtmlWebpackPlugin({
        template: "./index.html",
        filename: "index.html",
      }),
      new webpack.DefinePlugin({
        "process.env": JSON.stringify(appEnv),
      }),
    ],
    devServer: isProd
      ? undefined
      : {
          static: {
            directory: path.join(__dirname, "public"),
          },
          port: 5173,
          hot: true,
          open: true,
          historyApiFallback: true,
          proxy: {
            "/api": {
              target: "http://localhost:8080",
              changeOrigin: true,
            },
          },
        },
  };
};