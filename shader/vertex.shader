#version 330 core
in vec3 vertexv;
in vec4 colorv;
out vec4 color;
void main(){
    gl_Position = vertexv;
    color = colorv;
}